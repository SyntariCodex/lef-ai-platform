import os
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def model_fn(model_dir):
    """Load the model for inference"""
    model = AutoModelForCausalLM.from_pretrained(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    return model, tokenizer

def input_fn(request_body, request_content_type):
    """Parse input data for inference"""
    if request_content_type == 'application/json':
        input_data = json.loads(request_body)
        return input_data
    else:
        raise ValueError(f'Unsupported content type: {request_content_type}')

def predict_fn(input_data, model_and_tokenizer):
    """Make prediction using the input data"""
    model, tokenizer = model_and_tokenizer
    
    # Get parameters from environment variables
    max_length = int(os.environ.get('MAX_LENGTH', 512))
    top_k = int(os.environ.get('TOP_K', 50))
    top_p = float(os.environ.get('TOP_P', 0.95))
    do_sample = os.environ.get('DO_SAMPLE', 'True').lower() == 'true'
    
    # Prepare input text
    input_text = input_data.get('text', '')
    if not input_text:
        return {'error': 'No input text provided'}
    
    # Tokenize input
    inputs = tokenizer(input_text, return_tensors='pt', padding=True, truncation=True)
    
    # Generate response
    with torch.no_grad():
        outputs = model.generate(
            inputs['input_ids'],
            max_length=max_length,
            top_k=top_k,
            top_p=top_p,
            do_sample=do_sample,
            pad_token_id=tokenizer.pad_token_id,
            attention_mask=inputs['attention_mask']
        )
    
    # Decode response
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return {
        'response': response_text,
        'input_length': len(inputs['input_ids'][0]),
        'output_length': len(outputs[0])
    }

def output_fn(prediction, response_content_type):
    """Format the prediction response"""
    if response_content_type == 'application/json':
        return json.dumps(prediction)
    else:
        raise ValueError(f'Unsupported content type: {response_content_type}') 