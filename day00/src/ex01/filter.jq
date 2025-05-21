(["id", "created_at", "name", "has_test", "alternate_url"]) as $keys | ($keys | @csv), 
(.items[] | [.[ $keys[] ]] | @csv)