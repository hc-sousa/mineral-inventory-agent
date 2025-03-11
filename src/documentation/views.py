import os
import re
import markdown2
from django.shortcuts import render
from django.http import Http404

def collect_sections(docs_dir):
    """Collect all sections from the docs directory."""
    sections = []
    for dir_name in sorted(os.listdir(docs_dir)):
        dir_path = os.path.join(docs_dir, dir_name)
        if os.path.isdir(dir_path):
            parts = dir_name.split('_', 1)
            if len(parts) == 2 and parts[0].isdigit():
                _, section_name = parts
            else:
                section_name = dir_name

            sections.append({
                'section': section_name,
                'subsections': collect_subsections(dir_path)[0],
                'display_name': section_name.replace('_', ' ').title(),
                'dir_name': dir_name
            })
    return sections

def collect_subsections(section_dir, page='index'):
    """Collect subsections from the given section directory."""
    subsections = []
    markdown_file = None

    for f in sorted(os.listdir(section_dir)):
        if f.endswith('.md'):
            name = os.path.splitext(f)[0]
            parts = name.split('_', 1)
            if len(parts) == 2 and parts[0].isdigit():
                _, subsection_name = parts
            else:
                subsection_name = name

            subsections.append({
                'subsection': subsection_name,
                'display_name': subsection_name.replace('_', ' ').title(),
                'file': f,
                'path': os.path.join(re.sub(r'\d+_', '', os.path.basename(section_dir)), f)
            })

            if subsection_name == page:
                markdown_file = os.path.join(section_dir, f)

    if markdown_file is None or not os.path.exists(markdown_file):
        markdown_file = os.path.join(section_dir, 'index.md')
        if not os.path.exists(markdown_file):
            raise Http404("Documentation page not found.")

    return subsections, markdown_file

def docs_view(request, section='get_started', page='index'):
    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
    sections = collect_sections(docs_dir)

    section_dir = next((os.path.join(docs_dir, s['dir_name']) for s in sections if s['section'] == section), None)
    if section_dir is None or not os.path.isdir(section_dir):
        raise Http404("Documentation section not found.")

    subsections, markdown_file = collect_subsections(section_dir, page)

    with open(markdown_file, 'r', encoding='utf-8') as file:
        markdown_content = file.read()

    html_content = markdown2.markdown(markdown_content, extras=["fenced-code-blocks", "tables", "code-friendly"])

    return render(request, 'documentation/docs.html', {
        'content': html_content,
        'sections': sections,
        'subsections': subsections,
        'current_section': section,
        'current_page': page,
        'current_path': f"{section}/{os.path.basename(markdown_file)}",
        'section_display_name': section.replace('_', ' ').title(),
        'page_display_name': page.replace('_', ' ').title(),
        'page_title': f"{section.replace('_', ' ').title()} - {page.replace('_', ' ').title()}" if page != 'index' else section.replace('_', ' ').title()
    })

def search_docs(request):
    query = request.GET.get('q', '').strip()
    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
    sections = collect_sections(docs_dir)
    search_results = []

    if query:
        # Walk through the docs directory and search for the query in each .md file
        for root, dirs, files in os.walk(docs_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            # Get the section and page from the path
                            relative_path = os.path.relpath(file_path, docs_dir)
                            dir_name, _ = os.path.split(relative_path)

                            # Remove numeric prefix from the section name
                            section_parts = dir_name.split('/', 1)
                            if len(section_parts) == 2:
                                section_dir = section_parts[0]
                                subsection_file = section_parts[1].replace('.md', '')
                            else:
                                section_dir = dir_name
                                subsection_file = 'index'

                            section_name_parts = section_dir.split('_', 1)
                            if len(section_name_parts) == 2 and section_name_parts[0].isdigit():
                                _, section_name = section_name_parts
                            else:
                                section_name = section_dir

                            # Create a result entry
                            search_results.append({
                                'section': section_name,
                                'subsection': subsection_file,
                                'display_name': section_name.replace('_', ' ').title(),
                                'file_display_name': file.replace('.md', '').replace('_', ' ').title(),
                                'file_name': "_".join(file.replace('.md', '').split('_')[1:]),
                                'content_preview': get_content_preview(content, query),
                            })

    return render(request, 'documentation/search_results.html', {
        'query': query,
        'search_results': search_results,
        'page_title': 'Search Results',
        'sections': sections
    })

def get_content_preview(content, query, length=150):
    start = content.lower().find(query.lower())
    if start == -1:
        return content[:length]

    start = max(start - 20, 0)
    end = min(start + length, len(content))
    return content[start:end] + ('...' if end < len(content) else '')