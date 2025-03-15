import re
import json

def extract_mineral_data(response_text):
    """
    Extract structured mineral data from the response text if present
    """
    pattern = r'<MINERAL_DATA>(.*?)</MINERAL_DATA>'
    match = re.search(pattern, response_text, re.DOTALL)
    
    if match:
        try:
            # Extract the JSON string
            json_str = match.group(1).strip()
            
            # Ensure the JSON string is properly formatted with curly braces
            if not json_str.startswith("{"):
                json_str = "{" + json_str
            if not json_str.endswith("}"):
                json_str = json_str + "}"
                
            # Clean up the JSON string
            json_str = json_str.replace("\n", "").replace("\r", "")
            
            # Attempt to parse the JSON string
            try:
                mineral_data = json.loads(json_str)
                
                # Handle generic price field mapping
                if 'price' in mineral_data:
                    price = mineral_data['price']
                    # Determine where to map the price
                    pricing_type = mineral_data.get('pricing_type', 'fixed')
                    
                    if pricing_type == 'auction':
                        mineral_data['starting_price'] = price
                    else:
                        mineral_data['buy_now_price'] = price
                    
                # Handle dimensions if they're in a single field
                if 'dimensions' in mineral_data:
                    dims = mineral_data['dimensions']
                    # Try to parse dimensions like "18x20x2mm"
                    dim_match = re.search(r'(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)', dims)
                    if dim_match:
                        height, width, depth = dim_match.groups()
                        mineral_data['height'] = float(height)
                        mineral_data['width'] = float(width)
                        mineral_data['depth'] = float(depth)
                
                # Ensure price fields are properly formatted as numeric values
                price_fields = ['starting_price', 'reserve_price', 'buy_now_price']
                for field in price_fields:
                    if field in mineral_data:
                        # If string that can be converted to float, do so
                        if isinstance(mineral_data[field], str) and mineral_data[field].strip():
                            try:
                                mineral_data[field] = float(mineral_data[field])
                            except ValueError:
                                pass  # Keep as is if can't convert
                        
                        # If field is null or empty string, set to empty string for form
                        if mineral_data[field] is None or mineral_data[field] == "":
                            mineral_data[field] = ""
                
            except json.JSONDecodeError:
                # If still failing, try to clean up more aggressively
                json_str = re.sub(r'\s+', ' ', json_str)
                json_str = json_str.replace('": ', '":"').replace(', "', '","')
                json_str = json_str.replace('null', 'null"')
                json_str = json_str.replace(':"null"', ':null')
                mineral_data = json.loads(json_str)
            
            # Get the entire matched text (including tags)
            full_match = match.group(0)
            
            # Remove the entire match from the response text
            clean_response = response_text.replace(full_match, '').strip()
            
            print("Extracted JSON string:", json_str)
            print("Parsed mineral data:", mineral_data)
            print("Original length:", len(response_text), "Cleaned length:", len(clean_response))
            
            return clean_response, mineral_data
        except Exception as e:
            print(f"Error processing mineral data: {str(e)}")
            print(f"Problematic JSON string: {json_str if 'json_str' in locals() else 'Not extracted'}")
            # Return the original text without the tags in case of an error
            clean_response = re.sub(pattern, '', response_text, flags=re.DOTALL).strip()
            return clean_response, {}
    
    return response_text, {}