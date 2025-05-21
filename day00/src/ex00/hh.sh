#!/bin/sh
VACANCY=${1//' '/'-'}
curl -H 'User-Agent: user-agent' "https://api.hh.ru/vacancies?text=$VACANCY&per_page=20" | 
jq '{    
    page,
    found,
    clusters,
    arguments,
    per_page,
    pages,
    fixes,
    suggests,
    alternate_url,
    items
}' > hh.json