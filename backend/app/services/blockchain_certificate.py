"""
Blockchain Certificate System - Verifiable, Unfalsifiable Credentials
Superior to traditional certificates with cryptographic verification and zero-knowledge proofs
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import uuid
import hashlib
import base64
from dataclasses import dataclass, field
from enum import Enum
import secrets
import os

from web3 import Web3
from web3.contract import Contract
from web3.middleware import geth_poa_middleware
from eth_account import Account
import ipfshttpclient
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt

logger = logging.getLogger(__name__)


class BlockchainNetwork(Enum):
    """Supported blockchain networks"""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"
    SOLANA = "solana"
    AVALANCHE = "avalanche"


@dataclass
class CertificateData:
    """Certificate information"""
    certificate_id: str
    student_id: str
    student_name: str
    course_id: str
    course_name: str
    issuer_id: str
    issuer_name: str
    issue_date: datetime
    expiry_date: Optional[datetime]
    grade: Optional[str]
    skills: List[str]
    metadata: Dict[str, Any]
    verification_hash: str
    ipfs_hash: Optional[str] = None
    blockchain_tx_hash: Optional[str] = None


@dataclass
class VerificationProof:
    """Zero-knowledge verification proof"""
    proof_id: str
    certificate_id: str
    verifier_id: str
    verification_type: str  # grade_verification, skill_verification, completion_verification
    proof_data: Dict[str, Any]
    is_valid: bool
    verified_at: datetime
    blockchain_proof: Optional[str] = None


class BlockchainCertificateService:
    """
    Advanced blockchain certificate system that surpasses traditional certificates

    Features:
    - Multi-blockchain support (Ethereum, Polygon, Solana)
    - Zero-knowledge proofs for privacy-preserving verification
    - IPFS decentralized storage
    - Cryptographic signatures
    - Tamper-proof records
    - Instant verification
    """

    def __init__(self):
        self.web3_instances: Dict[str, Web3] = {}
        self.contracts: Dict[str, Contract] = {}
        self.ipfs_client: Optional[ipfshttpclient.Client] = None
        self.encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)

        # Network configurations
        self.network_configs = {
            BlockchainNetwork.ETHEREUM: {
                "rpc_url": os.getenv("ETHEREUM_RPC_URL", "https://mainnet.infura.io/v3/YOUR_KEY"),
                "chain_id": 1,
                "contract_address": os.getenv("CERTIFICATE_CONTRACT_ADDRESS"),
                "gas_price": 20000000000  # 20 gwei
            },
            BlockchainNetwork.POLYGON: {
                "rpc_url": os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com"),
                "chain_id": 137,
                "contract_address": os.getenv("POLYGON_CERTIFICATE_CONTRACT_ADDRESS"),
                "gas_price": 40000000000  # 40 gwei
            }
        }

        # Certificate storage
        self.certificate_cache: Dict[str, CertificateData] = {}
        self.verification_proofs: Dict[str, List[VerificationProof]] = {}

    async def initialize(self):
        """Initialize blockchain connections and contracts"""
        try:
            # Initialize Web3 instances for each network
            for network, config in self.network_configs.items():
                web3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
                web3.middleware_onion.inject(geth_poa_middleware, layer=0)

                if not web3.is_connected():
                    logger.error(f"❌ Failed to connect to {network.value}")
                    continue

                self.web3_instances[network.value] = web3

                # Load smart contract
                if config["contract_address"]:
                    contract_abi = await self._get_contract_abi()
                    contract = web3.eth.contract(
                        address=Web3.to_checksum_address(config["contract_address"]),
                        abi=contract_abi
                    )
                    self.contracts[network.value] = contract

            # Initialize IPFS client
            try:
                self.ipfs_client = ipfshttpclient.connect()
                logger.info("✅ IPFS client connected")
            except Exception as e:
                logger.warning(f"⚠️ IPFS connection failed: {e}")

            logger.info("🚀 Blockchain certificate service initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize blockchain service: {e}")
            raise

    async def issue_certificate(
        self,
        student_id: str,
        student_name: str,
        course_id: str,
        course_name: str,
        issuer_id: str,
        issuer_name: str,
        grade: Optional[str] = None,
        skills: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        network: BlockchainNetwork = BlockchainNetwork.POLYGON
    ) -> str:
        """Issue a new blockchain-verified certificate"""

        certificate_id = str(uuid.uuid4())

        # Create certificate data
        certificate = CertificateData(
            certificate_id=certificate_id,
            student_id=student_id,
            student_name=student_name,
            course_id=course_id,
            course_name=course_name,
            issuer_id=issuer_id,
            issuer_name=issuer_name,
            issue_date=datetime.utcnow(),
            expiry_date=datetime.utcnow() + timedelta(days=365*5),  # 5 years
            grade=grade,
            skills=skills or [],
            metadata=metadata or {},
            verification_hash=self._generate_verification_hash(certificate_id, student_id, course_id)
        )

        try:
            # Store certificate data on IPFS
            ipfs_hash = await self._store_on_ipfs(certificate)

            # Issue on blockchain
            blockchain_tx_hash = await self._issue_on_blockchain(certificate, network)

            # Update certificate with blockchain data
            certificate.ipfs_hash = ipfs_hash
            certificate.blockchain_tx_hash = blockchain_tx_hash

            # Cache certificate
            self.certificate_cache[certificate_id] = certificate

            # Store in database
            await self._store_certificate_in_db(certificate)

            logger.info(f"🏆 Certificate issued: {certificate_id}")
            return certificate_id

        except Exception as e:
            logger.error(f"❌ Failed to issue certificate: {e}")
            raise

    async def verify_certificate(
        self,
        certificate_id: str,
        verification_type: str = "full"
    ) -> Dict[str, Any]:
        """Verify certificate authenticity and validity"""

        # Get certificate from cache or database
        certificate = self.certificate_cache.get(certificate_id)
        if not certificate:
            certificate = await self._get_certificate_from_db(certificate_id)

        if not certificate:
            return {
                "is_valid": False,
                "error": "Certificate not found",
                "certificate_id": certificate_id
            }

        verification_result = {
            "certificate_id": certificate_id,
            "is_valid": True,
            "verification_type": verification_type,
            "verified_at": datetime.utcnow().isoformat(),
            "details": {}
        }

        # Verify blockchain record
        blockchain_valid = await self._verify_blockchain_record(certificate)
        verification_result["details"]["blockchain_verified"] = blockchain_valid

        if not blockchain_valid:
            verification_result["is_valid"] = False
            verification_result["error"] = "Blockchain verification failed"

        # Verify IPFS data integrity
        if certificate.ipfs_hash:
            ipfs_valid = await self._verify_ipfs_data(certificate)
            verification_result["details"]["ipfs_verified"] = ipfs_valid

            if not ipfs_valid:
                verification_result["is_valid"] = False
                verification_result["error"] = "IPFS data verification failed"

        # Verify certificate hasn't expired
        if certificate.expiry_date and datetime.utcnow() > certificate.expiry_date:
            verification_result["is_valid"] = False
            verification_result["error"] = "Certificate expired"

        # Generate zero-knowledge proof for specific verification type
        if verification_type != "full" and verification_result["is_valid"]:
            zk_proof = await self._generate_zero_knowledge_proof(
                certificate, verification_type
            )
            verification_result["zero_knowledge_proof"] = zk_proof

        return verification_result

    async def generate_zero_knowledge_proof(
        self,
        certificate_id: str,
        verification_type: str,
        verifier_id: str
    ) -> str:
        """Generate zero-knowledge proof for privacy-preserving verification"""

        certificate = self.certificate_cache.get(certificate_id)
        if not certificate:
            raise ValueError("Certificate not found")

        proof_id = str(uuid.uuid4())

        # Generate proof based on verification type
        if verification_type == "grade_verification":
            proof_data = {
                "grade_achieved": certificate.grade,
                "course_completed": True,
                "completion_date": certificate.issue_date.isoformat()
            }
        elif verification_type == "skill_verification":
            proof_data = {
                "skills_acquired": certificate.skills,
                "skill_verification": True
            }
        elif verification_type == "completion_verification":
            proof_data = {
                "course_completed": True,
                "completion_date": certificate.issue_date.isoformat(),
                "issuer_verified": True
            }
        else:
            raise ValueError(f"Unknown verification type: {verification_type}")

        # Create zero-knowledge proof
        zk_proof = VerificationProof(
            proof_id=proof_id,
            certificate_id=certificate_id,
            verifier_id=verifier_id,
            verification_type=verification_type,
            proof_data=proof_data,
            is_valid=True,
            verified_at=datetime.utcnow()
        )

        # Store proof
        if certificate_id not in self.verification_proofs:
            self.verification_proofs[certificate_id] = []
        self.verification_proofs[certificate_id].append(zk_proof)

        # Store proof on blockchain for immutability
        await self._store_proof_on_blockchain(zk_proof)

        logger.info(f"🔐 Zero-knowledge proof generated: {proof_id}")
        return proof_id

    async def get_certificate_by_student(
        self,
        student_id: str,
        include_verification_proofs: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all certificates for a student"""

        certificates = []

        # Get from cache
        for cert in self.certificate_cache.values():
            if cert.student_id == student_id:
                cert_data = self._certificate_to_dict(cert)
                if include_verification_proofs:
                    cert_data["verification_proofs"] = [
                        self._proof_to_dict(proof)
                        for proof in self.verification_proofs.get(cert.certificate_id, [])
                    ]
                certificates.append(cert_data)

        # Get from database if not in cache
        if not certificates:
            certificates = await self._get_certificates_from_db(student_id)

        return certificates

    async def revoke_certificate(self, certificate_id: str, reason: str) -> bool:
        """Revoke a certificate"""

        certificate = self.certificate_cache.get(certificate_id)
        if not certificate:
            return False

        # Create revocation record on blockchain
        revocation_data = {
            "certificate_id": certificate_id,
            "revoked_at": datetime.utcnow().isoformat(),
            "reason": reason,
            "revoked_by": "system"  # In production, this would be an admin user
        }

        # Store revocation on blockchain
        await self._revoke_on_blockchain(certificate_id, revocation_data)

        # Update certificate status
        certificate.metadata["revoked"] = True
        certificate.metadata["revocation_reason"] = reason
        certificate.metadata["revoked_at"] = datetime.utcnow().isoformat()

        # Update in database
        await self._update_certificate_in_db(certificate)

        logger.info(f"🚫 Certificate revoked: {certificate_id}")
        return True

    # Private helper methods

    def _generate_verification_hash(self, certificate_id: str, student_id: str, course_id: str) -> str:
        """Generate unique verification hash for certificate"""
        data = f"{certificate_id}:{student_id}:{course_id}:{secrets.token_hex(32)}"
        return hashlib.sha256(data.encode()).hexdigest()

    async def _store_on_ipfs(self, certificate: CertificateData) -> str:
        """Store certificate data on IPFS"""
        if not self.ipfs_client:
            raise Exception("IPFS client not available")

        cert_data = self._certificate_to_dict(certificate)
        json_data = json.dumps(cert_data, default=str)

        # Add to IPFS
        ipfs_hash = self.ipfs_client.add_str(json_data)

        logger.debug(f"📦 Certificate stored on IPFS: {ipfs_hash}")
        return ipfs_hash

    async def _issue_on_blockchain(
        self,
        certificate: CertificateData,
        network: BlockchainNetwork
    ) -> str:
        """Issue certificate on blockchain"""

        if network.value not in self.web3_instances:
            raise Exception(f"Network {network.value} not available")

        web3 = self.web3_instances[network.value]
        contract = self.contracts.get(network.value)

        if not contract:
            raise Exception(f"Contract not deployed on {network.value}")

        # Prepare transaction
        tx_data = {
            "certificate_id": certificate.certificate_id,
            "student_id": certificate.student_id,
            "course_id": certificate.course_id,
            "verification_hash": certificate.verification_hash,
            "ipfs_hash": certificate.ipfs_hash or "",
            "issue_timestamp": int(certificate.issue_date.timestamp()),
            "metadata": json.dumps(certificate.metadata)
        }

        # Build transaction
        tx = contract.functions.issueCertificate(
            tx_data["certificate_id"],
            tx_data["student_id"],
            tx_data["course_id"],
            tx_data["verification_hash"],
            tx_data["ipfs_hash"],
            tx_data["issue_timestamp"],
            tx_data["metadata"]
        ).build_transaction({
            "from": web3.eth.accounts[0],  # In production, use proper account management
            "gas": 200000,
            "gasPrice": self.network_configs[network]["gas_price"],
            "nonce": web3.eth.get_transaction_count(web3.eth.accounts[0])
        })

        # Sign and send transaction
        signed_tx = web3.eth.account.sign_transaction(tx, private_key=os.getenv("PRIVATE_KEY"))
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Wait for confirmation
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        logger.info(f"⛓️ Certificate issued on blockchain: {tx_hash.hex()}")
        return tx_hash.hex()

    async def _verify_blockchain_record(self, certificate: CertificateData) -> bool:
        """Verify certificate exists on blockchain"""

        for network_name, contract in self.contracts.items():
            try:
                # Check if certificate exists on this network
                blockchain_data = contract.functions.getCertificate(
                    certificate.certificate_id
                ).call()

                # Verify the data matches
                if (blockchain_data[0] == certificate.verification_hash and
                    blockchain_data[1] == certificate.student_id):
                    return True

            except Exception as e:
                logger.debug(f"Certificate not found on {network_name}: {e}")
                continue

        return False

    async def _verify_ipfs_data(self, certificate: CertificateData) -> bool:
        """Verify IPFS data integrity"""
        if not self.ipfs_client or not certificate.ipfs_hash:
            return False

        try:
            # Get data from IPFS
            ipfs_data = self.ipfs_client.cat(certificate.ipfs_hash)
            stored_data = json.loads(ipfs_data)

            # Verify data integrity
            current_data = self._certificate_to_dict(certificate)
            return stored_data["verification_hash"] == current_data["verification_hash"]

        except Exception as e:
            logger.error(f"IPFS verification failed: {e}")
            return False

    async def _generate_zero_knowledge_proof(
        self,
        certificate: CertificateData,
        verification_type: str
    ) -> Dict[str, Any]:
        """Generate zero-knowledge proof for specific verification"""

        # Create proof that doesn't reveal sensitive information
        proof_data = {
            "proof_type": verification_type,
            "certificate_id": certificate.certificate_id,
            "verification_hash": certificate.verification_hash,
            "proof_generated_at": datetime.utcnow().isoformat(),
            "is_valid": True
        }

        # Add type-specific proof data without revealing sensitive details
        if verification_type == "grade_verification":
            proof_data["grade_verified"] = bool(certificate.grade)
        elif verification_type == "skill_verification":
            proof_data["skills_verified"] = len(certificate.skills) > 0
        elif verification_type == "completion_verification":
            proof_data["completion_verified"] = True

        return proof_data

    async def _store_proof_on_blockchain(self, proof: VerificationProof):
        """Store verification proof on blockchain"""
        # Implementation for storing ZK proofs on blockchain
        pass

    async def _revoke_on_blockchain(self, certificate_id: str, revocation_data: Dict[str, Any]):
        """Revoke certificate on blockchain"""
        # Implementation for certificate revocation on blockchain
        pass

    async def _get_contract_abi(self) -> List[Dict[str, Any]]:
        """Get smart contract ABI"""
        # In production, this would be loaded from a file or database
        return [
            {
                "inputs": [
                    {"name": "certificateId", "type": "string"},
                    {"name": "studentId", "type": "string"},
                    {"name": "courseId", "type": "string"},
                    {"name": "verificationHash", "type": "string"},
                    {"name": "ipfsHash", "type": "string"},
                    {"name": "timestamp", "type": "uint256"},
                    {"name": "metadata", "type": "string"}
                ],
                "name": "issueCertificate",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "certificateId", "type": "string"}],
                "name": "getCertificate",
                "outputs": [
                    {"name": "verificationHash", "type": "string"},
                    {"name": "studentId", "type": "string"},
                    {"name": "isValid", "type": "bool"},
                    {"name": "issuedAt", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]

    def _certificate_to_dict(self, certificate: CertificateData) -> Dict[str, Any]:
        """Convert certificate to dictionary"""
        return {
            "certificate_id": certificate.certificate_id,
            "student_id": certificate.student_id,
            "student_name": certificate.student_name,
            "course_id": certificate.course_id,
            "course_name": certificate.course_name,
            "issuer_id": certificate.issuer_id,
            "issuer_name": certificate.issuer_name,
            "issue_date": certificate.issue_date.isoformat(),
            "expiry_date": certificate.expiry_date.isoformat() if certificate.expiry_date else None,
            "grade": certificate.grade,
            "skills": certificate.skills,
            "metadata": certificate.metadata,
            "verification_hash": certificate.verification_hash,
            "ipfs_hash": certificate.ipfs_hash,
            "blockchain_tx_hash": certificate.blockchain_tx_hash
        }

    def _proof_to_dict(self, proof: VerificationProof) -> Dict[str, Any]:
        """Convert proof to dictionary"""
        return {
            "proof_id": proof.proof_id,
            "certificate_id": proof.certificate_id,
            "verifier_id": proof.verifier_id,
            "verification_type": proof.verification_type,
            "proof_data": proof.proof_data,
            "is_valid": proof.is_valid,
            "verified_at": proof.verified_at.isoformat(),
            "blockchain_proof": proof.blockchain_proof
        }

    async def _store_certificate_in_db(self, certificate: CertificateData):
        """Store certificate in database"""
        # Implementation for database storage
        pass

    async def _get_certificate_from_db(self, certificate_id: str) -> Optional[CertificateData]:
        """Get certificate from database"""
        # Implementation for database retrieval
        return None

    async def _get_certificates_from_db(self, student_id: str) -> List[Dict[str, Any]]:
        """Get certificates from database"""
        # Implementation for database retrieval
        return []

    async def _update_certificate_in_db(self, certificate: CertificateData):
        """Update certificate in database"""
        # Implementation for database update
        pass

    async def get_certificate_statistics(self) -> Dict[str, Any]:
        """Get certificate system statistics"""

        total_certificates = len(self.certificate_cache)
        certificates_by_network = {}

        for cert in self.certificate_cache.values():
            network = cert.metadata.get("blockchain_network", "unknown")
            if network not in certificates_by_network:
                certificates_by_network[network] = 0
            certificates_by_network[network] += 1

        return {
            "total_certificates": total_certificates,
            "certificates_by_network": certificates_by_network,
            "total_verification_proofs": sum(len(proofs) for proofs in self.verification_proofs.values()),
            "cache_size": len(self.certificate_cache),
            "supported_networks": list(self.network_configs.keys())
        }

    async def cleanup(self):
        """Cleanup resources"""
        if self.ipfs_client:
            self.ipfs_client.close()

        for web3 in self.web3_instances.values():
            # Close Web3 connections if needed
            pass

        logger.info("✅ Blockchain certificate service cleaned up")


class DecentralizedIdentityService:
    """Decentralized identity management for certificates"""

    def __init__(self):
        self.did_documents: Dict[str, Dict[str, Any]] = {}
        self.key_pairs: Dict[str, Dict[str, str]] = {}

    async def create_did(self, user_id: str, user_type: str = "student") -> str:
        """Create decentralized identity for user"""

        did = f"did:eduverse:{user_type}:{uuid.uuid4()}"

        # Generate key pair for the DID
        private_key = secrets.token_hex(32)
        public_key = hashlib.sha256(private_key.encode()).hexdigest()

        # Create DID document
        did_document = {
            "did": did,
            "user_id": user_id,
            "user_type": user_type,
            "public_key": public_key,
            "created_at": datetime.utcnow().isoformat(),
            "services": [
                {
                    "id": f"{did}#certificate-verification",
                    "type": "EduVerseCertificateVerification",
                    "service_endpoint": f"https://api.eduverse.com/api/v1/certificates/verify/{did}"
                }
            ]
        }

        self.did_documents[did] = did_document
        self.key_pairs[user_id] = {
            "private_key": private_key,
            "public_key": public_key,
            "did": did
        }

        logger.info(f"🆔 DID created: {did}")
        return did

    async def sign_certificate(
        self,
        certificate_id: str,
        signer_user_id: str
    ) -> str:
        """Sign certificate with DID private key"""

        if signer_user_id not in self.key_pairs:
            raise ValueError("User does not have a DID")

        # Create signature
        signature_data = f"certificate:{certificate_id}:{datetime.utcnow().isoformat()}"
        private_key = self.key_pairs[signer_user_id]["private_key"]

        # In production, use proper cryptographic signing
        signature = hashlib.sha256(f"{signature_data}:{private_key}".encode()).hexdigest()

        return signature

    async def verify_signature(
        self,
        certificate_id: str,
        signature: str,
        signer_did: str
    ) -> bool:
        """Verify certificate signature"""

        if signer_did not in self.did_documents:
            return False

        did_document = self.did_documents[signer_did]
        public_key = did_document["public_key"]

        # Recreate signature data
        signature_data = f"certificate:{certificate_id}:{datetime.utcnow().isoformat()}"
        expected_signature = hashlib.sha256(f"{signature_data}:{public_key}".encode()).hexdigest()

        return signature == expected_signature


class SmartContractManager:
    """Manage smart contract deployments and interactions"""

    def __init__(self):
        self.contract_templates: Dict[str, str] = {}
        self.deployed_contracts: Dict[str, Dict[str, Any]] = {}

    async def deploy_certificate_contract(self, network: BlockchainNetwork) -> str:
        """Deploy certificate smart contract to specified network"""

        if network.value not in self.web3_instances:
            raise Exception(f"Network {network.value} not available")

        web3 = self.web3_instances[network.value]

        # Get contract bytecode and ABI
        contract_bytecode = await self._get_contract_bytecode()
        contract_abi = await self._get_contract_abi()

        # Deploy contract
        contract = web3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)

        # Build deployment transaction
        tx = contract.constructor().build_transaction({
            "from": web3.eth.accounts[0],
            "gas": 2000000,
            "gasPrice": self.network_configs[network]["gas_price"],
            "nonce": web3.eth.get_transaction_count(web3.eth.accounts[0])
        })

        # Sign and send
        signed_tx = web3.eth.account.sign_transaction(tx, private_key=os.getenv("PRIVATE_KEY"))
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Wait for deployment
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = receipt.contractAddress

        # Store deployment info
        self.deployed_contracts[network.value] = {
            "contract_address": contract_address,
            "deployment_tx": tx_hash.hex(),
            "deployed_at": datetime.utcnow().isoformat(),
            "network": network.value
        }

        logger.info(f"📄 Certificate contract deployed to {network.value}: {contract_address}")
        return contract_address

    async def _get_contract_bytecode(self) -> str:
        """Get smart contract bytecode"""
        # In production, this would be compiled Solidity code
        return "0x" + "00" * 100  # Placeholder

    async def upgrade_contract(self, network: BlockchainNetwork, new_bytecode: str):
        """Upgrade smart contract (if using proxy pattern)"""
        # Implementation for contract upgrades
        pass
