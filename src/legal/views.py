import json
import os
from django.shortcuts import render

from src import settings

def privacy_policy(request):
    return legal(request, load_legal_content('privacy_policy'))

def terms_of_service(request):    
    return legal(request, load_legal_content('terms_of_service'))

def licenses(request):
    return legal(request, load_legal_content('licenses'))   

def legal(request, context):
    with open(get_data_file_path('contact_info'), 'r') as file:
        contact_info = json.load(file)
        context.update(contact_info)
        context['product_name'] = settings.PROJECT_NAME
    return render(request, 'legal/legal.html', context)

def get_data_file_path(filename):
    return os.path.join(settings.BASE_DIR, 'legal', 'data', f'{filename}.json')

def load_legal_content(filename):
    def concatenate_content(content):
        if type(content) == list:
            return ' '.join(content)
        return content
    
    with open(get_data_file_path(filename), 'r') as file:
        content = json.load(file)
        for section in content['sections']:
            section['content'] = concatenate_content(section['content'])
            if 'subsections' in section:
                for subsection in section['subsections']:
                    subsection['content'] = concatenate_content(subsection['content'])
    return content