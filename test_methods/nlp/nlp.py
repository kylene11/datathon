import torch
from transformers import BertForTokenClassification, BertTokenizerFast

# Load the trained model
model = BertForTokenClassification.from_pretrained('./results')

# Load the tokenizer (use the same tokenizer you used for training)
tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')  # Or use 'bert-large-cased' if that's what you used

# Ensure the model is in evaluation mode (not training mode)
model.eval()

# Text to analyze
text = "The Kosovo citizen, Vendor 1 and Vendor 2 Representative, is the owner and Director of the Pristina-based Vendor 1 and also a 51% shareholder of the Pristina-Ljubljana-based company Vendor 2."

# Tokenize the input text
inputs = tokenizer(text, return_tensors="pt")

# Get predictions
with torch.no_grad():  # Disable gradient calculation for inference
    outputs = model(**inputs)

# Get the predicted labels for each token
predictions = outputs.logits.argmax(dim=-1)

# Decode the token IDs back to tokens
tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])

# Merge subwords for tokens that were split
merged_tokens = []
for token in tokens:
    if token.startswith("##"):
        # Remove '##' and merge with the previous token
        merged_tokens[-1] = merged_tokens[-1] + token[2:]
    else:
        merged_tokens.append(token)

# Print merged tokens and their corresponding predictions
for token, prediction in zip(merged_tokens, predictions[0].tolist()):
    print(f"Token: {token}, Label: {model.config.id2label[prediction]}")
