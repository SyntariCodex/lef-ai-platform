from lef.training.ai_training_model import AITrainingModel, TrainingSector
from lef.training.blockchain_integration import BlockchainIntegration, CredentialType
import time

def test_training_system():
    print("=== Testing Co Creator LLC Training System ===\n")
    
    # Initialize systems
    ai_model = AITrainingModel()
    blockchain = BlockchainIntegration()
    
    # Test trainee data
    trainee_id = "trainee_001"
    sector = TrainingSector.EARLY_EDUCATION
    
    print("1. Creating Learning Path...")
    learning_path = ai_model.create_learning_path(trainee_id, sector)
    print(f"Learning Path Created: {learning_path}\n")
    
    # Test skill assessment and updates
    print("2. Updating Skill Metrics...")
    assessment_data = {
        "classroom_management": 0.7,
        "curriculum_development": 0.6,
        "child_psychology": 0.8
    }
    metrics = ai_model.update_skill_metrics(trainee_id, assessment_data)
    print(f"Updated Metrics: {metrics}\n")
    
    # Test mentor matching
    print("3. Matching Mentor...")
    mentor = ai_model.match_mentor(trainee_id)
    print(f"Matched Mentor: {mentor}\n")
    
    # Test credential issuance
    print("4. Issuing Blockchain Credential...")
    credential = blockchain.issue_credential(
        trainee_id=trainee_id,
        credential_type=CredentialType.SKILL_CERTIFICATION,
        sector=sector.value,
        skills=list(assessment_data.keys()),
        issuer="Co Creator LLC"
    )
    print(f"Issued Credential: {credential}\n")
    
    # Test credential verification
    print("5. Verifying Credential...")
    verification = blockchain.verify_credential(credential.credential_id)
    print(f"Verification Result: {verification}\n")
    
    # Check trainee incentives
    print("6. Checking Training Incentives...")
    incentives = blockchain.get_trainee_incentives(trainee_id)
    print(f"Current Incentives: {incentives}\n")
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_training_system() 