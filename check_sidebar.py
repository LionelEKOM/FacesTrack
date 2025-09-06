#!/usr/bin/env python
"""
Script pour vérifier le contenu de la sidebar dans le template dashboard_teacher.html
"""
import re

def check_sidebar():
    """Vérifier le contenu de la sidebar"""
    
    with open('school/templates/dashboard_teacher.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire le bloc sidebar
    sidebar_match = re.search(r'{% block sidebar %}(.*?){% endblock %}', content, re.DOTALL)
    
    if sidebar_match:
        sidebar_content = sidebar_match.group(1)
        print("=== CONTENU DE LA SIDEBAR ===")
        print(sidebar_content)
        
        # Compter les éléments avec la classe 'active'
        active_count = sidebar_content.count('nav-link active')
        total_nav_links = sidebar_content.count('nav-link')
        
        print(f"\n=== ANALYSE ===")
        print(f"Total éléments nav-link: {total_nav_links}")
        print(f"Éléments avec classe 'active': {active_count}")
        
        if active_count == 1:
            print("✅ CORRECT: Seul un élément est actif")
        elif active_count == 0:
            print("⚠️ ATTENTION: Aucun élément n'est actif")
        else:
            print("❌ PROBLÈME: Plusieurs éléments sont actifs")
            
        # Vérifier les URLs
        print(f"\n=== URLS ===")
        urls = re.findall(r'href="([^"]*)"', sidebar_content)
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
            
    else:
        print("❌ Bloc sidebar non trouvé")

if __name__ == '__main__':
    check_sidebar()
