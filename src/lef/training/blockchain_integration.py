from typing import Dict, List, Optional
import time
import hashlib
import json
from dataclasses import dataclass
from enum import Enum

@dataclass
class Credential:
    credential_id: str
    trainee_id: str
    sector: str
    skills: List[str]
    issue_date: float
    expiry_date: Optional[float]
    issuer: str
    verification_hash: str

class CredentialType(Enum):
    SKILL_CERTIFICATION = "skill_certification"
    COURSE_COMPLETION = "course_completion"
    APPRENTICESHIP = "apprenticeship"
    MENTORSHIP = "mentorship"
    ASSESSMENT = "assessment"

class BlockchainIntegration:
    """Blockchain integration for credential verification and training incentives."""
    
    def __init__(self):
        self.credentials = {}  # credential_id -> Credential
        self.trainee_credentials = {}  # trainee_id -> List[credential_id]
        self.verification_chain = []  # List of credential verification blocks
        self.incentive_pool = {}  # trainee_id -> Dict[incentive_type, amount]
        
    def issue_credential(self, trainee_id: str, credential_type: CredentialType, 
                        sector: str, skills: List[str], issuer: str) -> Optional[Credential]:
        """Issue a new blockchain-verified credential."""
        try:
            # Generate unique credential ID
            timestamp = time.time()
            credential_id = hashlib.sha256(
                f"{trainee_id}:{sector}:{timestamp}".encode()
            ).hexdigest()
            
            # Create credential data
            credential_data = {
                'credential_id': credential_id,
                'trainee_id': trainee_id,
                'type': credential_type.value,
                'sector': sector,
                'skills': skills,
                'issue_date': timestamp,
                'issuer': issuer
            }
            
            # Generate verification hash
            verification_hash = self._generate_verification_hash(credential_data)
            
            # Create credential object
            credential = Credential(
                credential_id=credential_id,
                trainee_id=trainee_id,
                sector=sector,
                skills=skills,
                issue_date=timestamp,
                expiry_date=None,  # Set for time-limited credentials
                issuer=issuer,
                verification_hash=verification_hash
            )
            
            # Store credential
            self.credentials[credential_id] = credential
            if trainee_id not in self.trainee_credentials:
                self.trainee_credentials[trainee_id] = []
            self.trainee_credentials[trainee_id].append(credential_id)
            
            # Add to verification chain
            self._add_to_verification_chain(credential_data, verification_hash)
            
            # Issue training incentive
            self._issue_incentive(trainee_id, credential_type)
            
            return credential
            
        except Exception as e:
            print(f"Error issuing credential: {str(e)}")
            return None
    
    def verify_credential(self, credential_id: str) -> Dict:
        """Verify a credential on the blockchain."""
        try:
            credential = self.credentials.get(credential_id)
            if not credential:
                return {'verified': False, 'reason': 'Credential not found'}
            
            # Reconstruct verification hash
            credential_data = {
                'credential_id': credential.credential_id,
                'trainee_id': credential.trainee_id,
                'sector': credential.sector,
                'skills': credential.skills,
                'issue_date': credential.issue_date,
                'issuer': credential.issuer
            }
            
            current_hash = self._generate_verification_hash(credential_data)
            
            # Verify hash matches
            if current_hash != credential.verification_hash:
                return {'verified': False, 'reason': 'Verification hash mismatch'}
            
            # Check if credential is in verification chain
            chain_verified = self._verify_in_chain(credential.credential_id, credential.verification_hash)
            if not chain_verified:
                return {'verified': False, 'reason': 'Not found in verification chain'}
            
            return {
                'verified': True,
                'credential': credential_data,
                'verification_hash': current_hash
            }
            
        except Exception as e:
            print(f"Error verifying credential: {str(e)}")
            return {'verified': False, 'reason': str(e)}
    
    def get_trainee_credentials(self, trainee_id: str) -> List[Credential]:
        """Get all credentials for a trainee."""
        try:
            credential_ids = self.trainee_credentials.get(trainee_id, [])
            return [self.credentials[cred_id] for cred_id in credential_ids]
        except Exception as e:
            print(f"Error retrieving trainee credentials: {str(e)}")
            return []
    
    def get_trainee_incentives(self, trainee_id: str) -> Dict:
        """Get current incentive balance for trainee."""
        return self.incentive_pool.get(trainee_id, {})
    
    def _generate_verification_hash(self, data: Dict) -> str:
        """Generate verification hash for credential data."""
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def _add_to_verification_chain(self, credential_data: Dict, verification_hash: str):
        """Add credential to verification chain."""
        block = {
            'timestamp': time.time(),
            'credential_id': credential_data['credential_id'],
            'verification_hash': verification_hash,
            'previous_hash': self.verification_chain[-1]['verification_hash'] if self.verification_chain else None
        }
        self.verification_chain.append(block)
    
    def _verify_in_chain(self, credential_id: str, verification_hash: str) -> bool:
        """Verify credential exists in verification chain."""
        return any(
            block['credential_id'] == credential_id and 
            block['verification_hash'] == verification_hash 
            for block in self.verification_chain
        )
    
    def _issue_incentive(self, trainee_id: str, credential_type: CredentialType):
        """Issue training incentive for credential achievement."""
        if trainee_id not in self.incentive_pool:
            self.incentive_pool[trainee_id] = {}
            
        # Define incentive amounts for different credential types
        incentive_amounts = {
            CredentialType.SKILL_CERTIFICATION: 100,
            CredentialType.COURSE_COMPLETION: 50,
            CredentialType.APPRENTICESHIP: 200,
            CredentialType.MENTORSHIP: 75,
            CredentialType.ASSESSMENT: 25
        }
        
        amount = incentive_amounts.get(credential_type, 0)
        if amount > 0:
            current_amount = self.incentive_pool[trainee_id].get(credential_type.value, 0)
            self.incentive_pool[trainee_id][credential_type.value] = current_amount + amount 