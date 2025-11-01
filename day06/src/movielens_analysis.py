import requests
import json
import datetime
import re
from bs4 import BeautifulSoup
import collections
import re
from collections import defaultdict
import os

# --------------------------- Links ----------------------------

class Links:
    def __init__(self, path_to_the_file, output_file, list_of_fields):
        # Инициализирует объект, загружает данные из входного файла с ID фильмов.
        self.file = path_to_the_file
        self.output_file = output_file
        self.data = self._load_data(self.file)
        self.list_of_fields = self._load_fields(list_of_fields)
        self.get_imdb()

    def _load_data(self, list_of_movies): 
        # Загружает список IMDb ID из CSV-файла.
        imdb_ids = []

        with open(list_of_movies, 'r', encoding='utf-8') as file:
            next(file)
            for line in file:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    imdb_id = parts[1]
                    if imdb_id.isdigit():
                        imdb_ids.append(imdb_id)

        return imdb_ids

    def _load_fields(self, list_of_fields):
        # Загружает список нужных полей из текстового файла.
        fields = []

        with open(list_of_fields, 'r', encoding='utf-8') as file: 
            line = file.read()
            fields = line.strip().split(',')

        return fields

    def get_imdb(self):
        # Собирает информацию о фильмах с IMDb по заданным полям и сохраняет результат.
        if os.stat(self.output_file).st_size == 0:
            # Если файл output не пустой, только тогда начинается парсинг
            imdb_ids = self.data
            fields = self.list_of_fields
            imdb_info = []
            
            for idx, id in enumerate(imdb_ids, start=1):
                film_info = [id]
                soup = self._get_soup(id)
                if 'Director' in fields or 'Title' in fields:
                    director, title = self._extract_metadata(soup)
                    if 'Director' in fields:
                        film_info.append(director)
                    if 'Title' in fields:    
                        film_info.append(title)
                if 'Budget' in fields or 'Cumulative Worldwide Gross' in fields: 
                    budget, worldwide_gross = self._extract_financials(soup)
                    if 'Budget' in fields: 
                        film_info.append(str(budget))
                    if 'Cumulative Worldwide Gross' in fields:
                        film_info.append(str(worldwide_gross))
                if 'Runtime' in fields:
                    runtime = self._extract_runtime(soup)
                    film_info.append(runtime)
                # print(f"{idx}: информация о фильме {title} добавлена")
                imdb_info.append(film_info)

            self._safe_result(imdb_info, fields)
            return imdb_info  # Важно: возвращаем результат
        return None
        
    def _get_soup(self, id):
        # Загружает HTML-страницу фильма с IMDb и возвращает объект BeautifulSoup.
        url = f"https://www.imdb.com/title/tt{id}/" 
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def _extract_metadata(self, soup):
        # Извлекает название фильма и имя режиссёра из метаданных.
        director = "N/A"
        title = "N/A"

        script = soup.find('script', type='application/ld+json')
        if script:
            try:
                data = json.loads(script.string)
                director_data = data.get('director')
                if director_data and isinstance(director_data, list) and len(director_data) > 0:
                    director = director_data[0].get('name', 'N/A')
                title = data.get('name', 'N/A')
            except:
                pass  # Игнорируем любые ошибки парсинга

        return director, title

    def _extract_financials(self, soup):
        # Извлекает бюджет и мировые сборы фильма.
        CLEAN_NUMBERS = re.compile(r"[^\d]")
        box_office_data = {}
        box_office_section = soup.find('section', {'data-testid': 'BoxOffice'})

        if not box_office_section:
            budget = 'N/A'
            worldwide_gross = 'N/A'
            return budget, worldwide_gross

        for row in box_office_section.select('li'):
            label = row.select_one('span.ipc-metadata-list-item__label')
            value = row.select_one('span.ipc-metadata-list-item__list-content-item')
            if label and value:
                text = label.text.strip()
                val = CLEAN_NUMBERS.sub("", value.text.strip())
                if "Budget" in text:
                    box_office_data["budget"] = int(val) if val else "N/A"
                elif "Gross worldwide" in text:
                    box_office_data["worldwide_gross"] = int(val) if val else "N/A"

        budget = box_office_data.get("budget", "N/A")
        worldwide_gross = box_office_data.get("worldwide_gross", "N/A")
        return budget, worldwide_gross

    def _extract_runtime(self, soup):
        # Извлекает продолжительность фильма в минутах.
        runtime_element = soup.find('li', {'data-testid': 'title-techspec_runtime'})
        if not runtime_element:
            return "N/A"

        runtime_str = runtime_element.find('div').text.strip()
        numbers = list(map(int, re.findall(r'\d+', runtime_str)))

        if not numbers:
            return "N/A"
        
        if len(numbers) == 2: 
            return f"{numbers[0] * 60 + numbers[1]}"
        elif len(numbers) == 1:  
            if 'h' in runtime_str:
                return f"{numbers[0] * 60}"
            else: 
                return f"{numbers[0]}"
        else:
            return "N/A"  # На случай нестандартного формата
    
    def _safe_result(self, list_result, fields):
        # Сохраняет собранные данные в CSV-файл и сортирует его.
        with open(self.output_file, "w", encoding='utf-8') as f:
            f.write(",".join(fields) + "\n")
            for line in list_result:
                f.write("*".join(line) + "\n")
        self._sort_result()

    def _sort_result(self):
        # Сортирует CSV-файл по убыванию ID фильма.
        with open(self.output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        header = lines[0]
        data_lines = lines[1:]
        sorted_lines = sorted(data_lines, key=lambda line: line.split('*')[0], reverse=True)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(header)
            f.writelines(sorted_lines)

    def _read_movie_data(self):
        # Читает и парсит данные фильмов из выходного CSV-файла.
        movies = []
        exclude_titles = {'N/A', 'NOT AVAILABLE', 'UNKNOWN'}
        with open(self.output_file, 'r', encoding='utf-8') as f:
            next(f)  
            for line in f:
                parts = line.strip().split('*')
                if len(parts) >= 6:
                    try:
                        movie_data = {
                            'id': parts[0].strip(),
                            'director': parts[1].strip(),
                            'title': parts[2].strip(),
                            'budget': int(parts[3].strip()) if parts[3].strip() != 'N/A' else 'N/A',
                            'gross': int(parts[4].strip()) if parts[4].strip() != 'N/A' else 0,
                            'runtime': int(parts[5].strip()) if parts[5].strip() != 'N/A' else 0
                        }
                        if movie_data['title'] not in exclude_titles:
                            movies.append(movie_data)
                    except (ValueError, IndexError) as e:
                        print(f"Ошибка обработки строки: {line}. Ошибка: {e}")
                        continue
        return movies
    
    def top_directors(self, n):
        # Находит топ-N режиссёров по количеству фильмов.
        director_counts = defaultdict(int)
        movies = self._read_movie_data()
        for movie in movies:
            if movie['director'] and movie['director'] != 'N/A':
                director_counts[movie['director']] += 1

        sorted_directors = sorted(director_counts.items(), key=lambda item: item[1], reverse=True)
        return dict(sorted_directors[:n])


    def most_expensive(self, n):
        # Находит топ-N фильмов с самым большим бюджетом.
        movies = self._read_movie_data()
        valid_movies = []
        for m in movies:
            budget = m.get('budget')
            try:
                budget_float = float(budget) if budget not in ['N/A', '', None] else None
                if budget_float and budget_float >= 0: 
                    valid_movies.append(m)
            except (ValueError, TypeError):
                continue
        sorted_movies = sorted(valid_movies, key=lambda x: x['budget'], reverse=True)
        top_movies = {movie['title']: movie['budget'] for movie in sorted_movies[:n]}
        return top_movies
    
    def the_cheapest(self, n):
        movies = self._read_movie_data()
    
        # Filter movies with valid budgets
        valid_movies = []
        for movie in movies:
            budget = movie.get('budget')
            if isinstance(budget, (int, float)) and budget >= 0:  # Only allow numeric budgets >= 0
                valid_movies.append(movie)
        
        # Sort by budget (ascending) and take top N
        sorted_movies = sorted(valid_movies, key=lambda x: x['budget'], reverse=False)
        top_movies = {movie['title']: movie['budget'] for movie in sorted_movies[:n]}
        
        return top_movies
    
    def most_profitable(self, n):
        # Находит топ-N самых прибыльных фильмов.
        
        movies = self._read_movie_data()
        valid_movies = []

        for movie in movies:
            if not isinstance(movie.get('budget'), (int, float)) or not isinstance(movie.get('gross'), (int, float)):
                continue
            
            if movie['budget'] <= 0 or movie['gross'] <= 0:
                continue
            
            movie_copy = movie.copy()
            movie_copy['profit'] = movie_copy['gross'] - movie_copy['budget']
            valid_movies.append(movie_copy)

        sorted_movies = sorted(valid_movies, key=lambda x: x['profit'], reverse=True)[:n]
 
        top_movies = {movie['title']: movie['profit'] for movie in sorted_movies}
        
        return top_movies
    
    def less_profitable(self, n): # Дополнительная функция
        # Находит топ-N менее прибыльных фильмов.
        movies = self._read_movie_data()
        valid_movies = []

        for movie in movies:
            if not isinstance(movie.get('budget'), (int, float)) or not isinstance(movie.get('gross'), (int, float)):
                continue
            
            if movie['budget'] <= 0 or movie['gross'] <= 0:
                continue
            
            movie_copy = movie.copy()
            movie_copy['profit'] = movie_copy['gross'] - movie_copy['budget']
            valid_movies.append(movie_copy)

        sorted_movies = sorted(valid_movies, key=lambda x: x['profit'], reverse=False)[:n]
 
        top_movies = {movie['title']: movie['profit'] for movie in sorted_movies}
        
        return top_movies

    def longest(self, n):
        # Находит топ-N самых длинных фильмов по продолжительности.
        movies = self._read_movie_data()
        sorted_movies = sorted(movies, key=lambda x: x['runtime'], reverse=True)
        top_movies = {movie['title']: movie['runtime'] for movie in sorted_movies[:n]}
        return top_movies
    
    def shortest(self, n): # Дополнительная функция
        # Находит топ-N самых длинных фильмов по продолжительности.
        movies = self._read_movie_data()
        sorted_movies = sorted(movies, key=lambda x: x['runtime'], reverse=False)
        top_movies = {movie['title']: movie['runtime'] for movie in sorted_movies[:n]}
        return top_movies

    def top_cost_per_minute(self, n):
        # Находит топ-N фильмов с самой высокой стоимостью за минуту.
        movies = self._read_movie_data()
        valid_movies = []
        for movie in movies:
            if not isinstance(movie.get('budget'), (int, float)) or not isinstance(movie.get('gross'), (int, float)):
                continue

            if movie['budget'] > 0 and movie['runtime'] > 0:
                movie_copy = movie.copy()
                movie_copy['cost_per_minute'] = round(movie_copy['budget'] / max(1, movie_copy['runtime']), 2)
                valid_movies.append(movie_copy)
        
        sorted_movies = sorted(valid_movies, key=lambda x: x['cost_per_minute'], reverse=True)
        top_movies = {movie['title']: movie['cost_per_minute'] for movie in sorted_movies[:n]}
        return top_movies
    
    def less_cost_per_minute(self, n): # Дополнительная функция
        # Находит топ-N фильмов с самой низкой стоимостью за минуту.
        movies = self._read_movie_data()
        valid_movies = []
        for movie in movies:
            if not isinstance(movie.get('budget'), (int, float)) or not isinstance(movie.get('gross'), (int, float)):
                continue

            if movie['budget'] > 0 and movie['runtime'] > 0:
                movie_copy = movie.copy()
                movie_copy['cost_per_minute'] = round(movie_copy['budget'] / max(1, movie_copy['runtime']), 2)
                valid_movies.append(movie_copy)
        
        sorted_movies = sorted(valid_movies, key=lambda x: x['cost_per_minute'], reverse=False)
        top_movies = {movie['title']: movie['cost_per_minute'] for movie in sorted_movies[:n]}
        return top_movies
    
    def top_longest_title(self, n):
        # Находит топ-N фильмов с самым длинным названием
        movies = self._read_movie_data()
        sorted_movies = sorted(movies, key=lambda x: len(x['title']), reverse=True)
        top_movies = [movie['title'] for movie in sorted_movies[:n]]
        return top_movies
    
    def top_shortest_title(self, n): # Дополнительная функция
        # Находит топ-N фильмов с самым коротким названием
        movies = self._read_movie_data()
        sorted_movies = sorted(movies, key=lambda x: len(x['title']), reverse=False)
        top_movies = [movie['title'] for movie in sorted_movies[:n]]
        return top_movies
    

# --------------------------- Movies ----------------------------

class Movies:
    """
    Analyzing data from movies.csv
    """
    def __init__(self, path_to_the_file):
        """
        Put here any fields that you think you will need.
        """
        self.source = self.get_data(path_to_the_file)

    def get_data(self, path):
        movies = []
        with open(path, mode='r', encoding='utf-8') as file:
            reader = file.readlines()
        headers = reader[0][:-1].split(',')
        text = reader[1:]
        pattern = r'"(.*?)"'
        parts = []
        for line in text:
            res = re.findall(pattern, line)
            if res:
                parts = line.split('"')
                if len(res) > 1:
                    parts[1] = ''.join(res)
                    parts[2] = parts[-1]
                parts[0] = parts[0][:-1]
                parts[2] = parts[2][1:-1]
            else:
                parts = line.split(',')
                parts[2] = parts[2][:-1]

            d = {headers[0]: parts[0],
                headers[1]: parts[1],
                headers[2]: parts[2].split('|'),
                'year': self.get_year(parts[1])}
            movies.append(d)
        return movies
    
    def get_year(self, title):
        res = re.findall(r'\((\d{4})\)', title)
        return int(*res)
    
    def to_json(self, path):
        with open(path, mode='w', encoding='utf-8') as file:
            json.dump(self.source, file, ensure_ascii=False, indent=4)

    def dist_by_release(self): # Распределение по годам
        """
        The method returns a dict or an OrderedDict where the keys are years and the values are counts. 
        You need to extract years from the titles. Sort it by counts descendingly.
        """
        release_years = {}
        for movie in self.source:
            if movie['year'] not in release_years.keys():
                release_years[movie['year']] = 1
            else:
                release_years[movie['year']] += 1

        sort_by_count = sorted(release_years.items(), key=lambda item: item[1], reverse=True)
        release_years = dict(sort_by_count)
        return release_years
    
    def dist_by_genres(self): # Распределение по жанрам
        """
        The method returns a dict where the keys are genres and the values are counts.
        Sort it by counts descendingly.
        """
        genres = {}
        for movie in self.source:
            for genre in movie['genres']:
                if genre not in genres.keys():
                    genres[genre] = 1
                else:
                    genres[genre] += 1
        
        genres = dict(sorted(genres.items(), key=lambda item: item[1], reverse=True))

        return genres
        
    def most_genres(self, n): # N фильмов с наибольшим количеством жанров
        """
        The method returns a dict with top-n movies where the keys are movie titles and 
        the values are the number of genres of the movie. Sort it by numbers descendingly.
        """
        movies = {}
        if n > 0:
            for movie in self.source:
                movies[movie['title']] = len(movie['genres'])

            movies = dict(sorted(movies.items(), key=lambda item: item[1], reverse=True)[:n])

        return movies
    
    def genre_filter(self, list_of_genres): 
        """
        The method returns a list of films with all given genres
        """
        movies = []
        if len(list_of_genres) > 0:
            for movie in self.source:
                if all(element in movie['genres'] for element in list_of_genres):
                    movies.append(movie['title'])

        return movies
    
    def genre_correlation(self, genre, n): 
        """
        The method returns a dict of n genres that are most frequently
        correlated with a given genre
        """
        corr = {}
        if n > 0:
            corr[genre] = {}
            for movie in self.source:
                if genre in movie['genres']:
                    for g in movie['genres']:
                        if g != genre and g not in corr[genre].keys():
                            corr[genre][g] = 1
                        elif g != genre:
                            corr[genre][g] += 1
            
            corr[genre] = dict(sorted(corr[genre].items(), key=lambda item: item[1], reverse=True)[:n])

        return corr
    
    def genre_frequency_by_year(self, n): 
        """
        The method returns a dict of n most popular
        genres for every year
        """
        years = {}
        if n > 0:
            for movie in self.source:
                if movie['year'] not in years.keys():
                    years[movie['year']] = {}
                for genre in movie['genres']:
                    if genre not in years[movie['year']].keys():
                        years[movie['year']][genre] = 1
                    else:
                        years[movie['year']][genre] += 1

            for year in years.keys():
                years[year] = dict(sorted(years[year].items(), key=lambda item: item[1], reverse=True)[:n])
        return years

    def definite_genre_frequency_by_year(self, genre): 
        """
        The method returns a dict of years and counts of given genre
        """
        freq = {}
        freq[genre] = {}
        for movie in self.source:
            if genre in movie['genres']:
                if movie['year'] not in freq[genre].keys():
                    freq[genre][movie['year']] = 1
                else:
                    freq[genre][movie['year']] += 1

        freq[genre] = dict(sorted(freq[genre].items(), key=lambda item: item[1], reverse=True))
        return freq

# --------------------------- Tags ----------------------------

class Tags:
    """
    Analyzing data from tags.csv
    """
    def __init__(self, path_to_the_file):
        """
        Put here any fields that you think you will need.
        """
        self.source = self.get_data(path_to_the_file)

    def get_data(self, path):
        tags = []
        with open(path, mode='r', encoding='utf-8') as file:
            reader = file.readlines()
        headers = reader[0][:-1].split(',')
        text = reader[1:]
        parts = []
        for line in text:
            parts = line.split(',')
            date = datetime.datetime.fromtimestamp(int(parts[3][:-1]))
            d = {headers[0]: int(parts[0]),
                 headers[1]: int(parts[1]),
                 headers[2]: parts[2].title(),
                 headers[3]: date.strftime('%Y-%m-%d %H:%M:%S').split(' '),
                 'year': date.year}
            tags.append(d)
        return tags
    
    def to_json(self, path):
        with open(path, mode='w', encoding='utf-8') as file:
            json.dump(self.source, file, ensure_ascii=False, indent=4)

    def most_words(self, n): # Топ тэгов из наибольшего количества слов
        """
        The method returns top-n tags with most words inside. It is a dict 
        where the keys are tags and the values are the number of words inside the tag.
        Drop the duplicates. Sort it by numbers descendingly.
        """
        big_tags = {}
        if n > 0:
            for tag in self.source:
                big_tags[tag['tag']] = len(tag['tag'].split(' '))

            big_tags = dict(sorted(big_tags.items(), key=lambda item: item[1], reverse=True)[:n])

        return big_tags

    def longest(self, n): # Топ самых длинных
        """
        The method returns top-n longest tags in terms of the number of characters.
        It is a list of the tags. Drop the duplicates. Sort it by numbers descendingly.
        """
        big_tags = []
        tags = {}
        if n > 0:
            for tag in self.source:
                tags[tag['tag']] = len(tag['tag'])

            tags = dict(sorted(tags.items(), key=lambda item: item[1], reverse=True)[:n])
            big_tags = list(tags.keys())
        return big_tags

    def most_words_and_longest(self, n): # Пересечение возвратов первого и второго метода
        """
        The method returns the intersection between top-n tags with most words inside and 
        top-n longest tags in terms of the number of characters.
        Drop the duplicates. It is a list of the tags.
        """
        big_tags = []
        if n > 0:
            most_words = set(self.most_words(n))
            longest = set(self.longest(n))
            big_tags = sorted(list(most_words.intersection(longest)))
        return big_tags
        
    def most_popular(self, n): # Самые популярные
        """
        The method returns the most popular tags. 
        It is a dict where the keys are tags and the values are the counts.
        Drop the duplicates. Sort it by counts descendingly.
        """
        popular_tags = {}
        if n > 0:
            for tag in self.source:
                if tag['tag'] not in popular_tags.keys():
                    popular_tags[tag['tag']] = 1
                else:
                    popular_tags[tag['tag']] += 1
            
            popular_tags = dict(sorted(popular_tags.items(), key=lambda item: item[1], reverse=True)[:n])

        return popular_tags
        
    def tags_with(self, word): # Тэги с указанным словом
        """
        The method returns all unique tags that include the word given as the argument.
        Drop the duplicates. It is a list of the tags. Sort it by tag names alphabetically.
        """
        tags_with_word = set()
        for tag in self.source:
            if word.title() in tag['tag'].split(' '):
                tags_with_word.add(tag['tag'])
        tags_with_word = sorted(list(tags_with_word))
        return tags_with_word
    
    def most_popular_by_year(self, year, n):
        """
        The method returns top-n most popular tags in the given year.
        It is a dict where the keys are tags and the values are the counts.
        """
        popular_tags = {}
        if n > 0:
            for tag in self.source:
                if tag['year'] == year:
                    if tag['tag'] not in popular_tags.keys():
                        popular_tags[tag['tag']] = 1
                    else:
                        popular_tags[tag['tag']] += 1
            
            popular_tags = dict(sorted(popular_tags.items(), key=lambda item: item[1], reverse=True)[:n])

        return popular_tags
    
    def tags_for_years(self):
        """
        The method returns a dict where the keys are years and the values are the numbers of tags.
        """
        tagged_years = {}
        for tag in self.source:
            if tag['year'] not in tagged_years.keys():
                tagged_years[tag['year']] = 1
            else:
                tagged_years[tag['year']] += 1
        
        tagged_years = dict(sorted(tagged_years.items(), key=lambda item: item[1], reverse=True))

        return tagged_years
    
    def count_definite_by_year(self, list_of_tags):
        """
        The method returns a dict where the keys are given tags and the values are the counts by years.
        """
        if len(list_of_tags) > 0:
            list_of_tags = [s.title() for s in list_of_tags]
            tags = {key: {} for key in list_of_tags}
            for tag in self.source:
                if tag['tag'] in tags.keys():
                    if tag['year'] not in tags[tag['tag']].keys():
                        tags[tag['tag']][tag['year']] = 1
                    else:
                        tags[tag['tag']][tag['year']] += 1
        else:
            tags = {}
        return tags
    
    def tag_count_by_distinct_users(self, n):
        """
        The method returns a dict with top-n tags where the keys are tags and the values are the counts
        by only distinct users. Shows how many distinct people use these tags.
        """
        counts = {}
        if n > 0 :
            for tag in self.source:
                if tag['tag'] not in counts.keys():
                    counts[tag['tag']] = set()
                counts[tag['tag']].add(tag['userId'])
            
            for tag in counts.keys():
                counts[tag] = len(counts[tag])
            
            counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True)[:n])

        return counts
    

    def distinct_tag_count_by_distinct_users(self, t):
        """
        Shows how many distinct people use given tag.
        """
        counts = {}
        for tag in self.source:
            if tag['tag'] not in counts.keys():
                counts[tag['tag']] = set()
            counts[tag['tag']].add(tag['userId'])
        
        for tag in counts.keys():
            counts[tag] = len(counts[tag])
        
        if t not in counts.keys():
            return 0
        return counts[t]
    
    def tag_count_by_distinct_movies(self, n):
        """
        The method returns a dict with top-n tags where the keys are tags and the values are the counts
        by only distinct users. Shows how many there are distinct movies with these tags.
        """
        counts = {}
        if n > 0:
            for tag in self.source:
                if tag['tag'] not in counts.keys():
                    counts[tag['tag']] = set()
                counts[tag['tag']].add(tag['movieId'])
            
            for tag in counts.keys():
                counts[tag] = len(counts[tag])
            
            counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True)[:n])

        return counts


# --------------------------- Ratings ----------------------------

# вспомогательные функции
def average(nums):
    return sum(nums) / len(nums) if nums else 0.0

def median(nums):
    nums = sorted(nums)
    n = len(nums)
    mid = n // 2
    return nums[mid] if n % 2 else (nums[mid - 1] + nums[mid]) / 2

def variance(nums):
    m = average(nums)
    return sum((x - m) ** 2 for x in nums) / len(nums) if nums else 0.0


class Ratings:
    """
    Analyzing data from ratings.csv
    """
    # --------------------------- Загрузка данных ----------------------------
    def __init__(self, path_to_the_file):
        """
        Сохраняем данные и строим словарь movieId → title (по movies.csv,
        лежащему в той же папке, что ratings.csv).
        """
        self.ratings = self._load_ratings(path_to_the_file)
        self.movie_titles = self._load_movie_titles(path_to_the_file)

    def _load_ratings(self, path):
        data = []
        with open(path, "r", encoding="utf-8") as f:
            next(f)                       # пропускаем заголовок
            for line in f:
                if not line.strip():
                    continue
                parts = line.rstrip("\n").split(",")
                if len(parts) != 4:
                    continue
                uid, mid, rating, ts = parts
                year = datetime.datetime.fromtimestamp(int(ts)).year
                data.append(
                    {
                        "userId": int(uid),
                        "movieId": int(mid),
                        "rating": float(rating),
                        "timestamp": int(ts),
                        "year": year,
                    }
                )
        return data


    def _load_movie_titles(self, ratings_path):
        import os
        base = os.path.dirname(ratings_path)
        movies_path = os.path.join(base, "movies.csv")
        titles = {}
        try:
            with open(movies_path, "r", encoding="utf-8") as f:
                next(f)
                for line in f:
                    if not line.strip():
                        continue
                    parts = line.rstrip("\n").rsplit(",", maxsplit=1)
                    if len(parts) < 2:
                        continue
                    left_joined, _genres = parts
                    if "," not in left_joined:
                        continue
                    mid, title = left_joined.split(",", maxsplit=1)
                    titles[int(mid)] = title.strip().strip('"')
        except FileNotFoundError:
            pass
        return titles


    # ---------------------------- Movies ------------------------------
    class Movies:
        def __init__(self, parent):
            self._r = parent.ratings
            self._titles = parent.movie_titles

        def dist_by_year(self):  # Количество оценок в год
            """
            The method returns a dict where the keys are years and the values are counts. 
            Sort it by years ascendingly. You need to extract years from timestamps.
            """
            ratings_by_year = collections.defaultdict(int)
            for row in self._r:
                ratings_by_year[row["year"]] += 1
            ratings_by_year = dict(sorted(ratings_by_year.items()))
            return ratings_by_year

        def dist_by_rating(self):  # Количество тех или иных оценок
            """
            The method returns a dict where the keys are ratings and the values are counts.
            Sort it by ratings ascendingly.
            """
            ratings_distribution = collections.defaultdict(int)
            for row in self._r:
                ratings_distribution[row["rating"]] += 1
            ratings_distribution = dict(sorted(ratings_distribution.items()))
            return ratings_distribution

        def top_by_num_of_ratings(self, n):  # Топ самых оцениваемых
            """
            The method returns top-n movies by the number of ratings. 
            It is a dict where the keys are movie titles and the values are numbers.
            Sort it by numbers descendingly.
            """
            counts = collections.defaultdict(int)
            for row in self._r:
                counts[row["movieId"]] += 1
            top_movies = sorted(
                counts.items(), key=lambda kv: kv[1], reverse=True
            )[:n]
            top_movies = {
                self._titles.get(mid, f"Movie {mid}"): cnt for mid, cnt in top_movies
            }
            return top_movies

        def top_by_ratings(self, n, metric=average):  # Топ по средней оценке (или медиане оценок) 
            """
            The method returns top-n movies by the average or median of the ratings.
            It is a dict where the keys are movie titles and the values are metric values.
            Sort it by metric descendingly.
            The values should be rounded to 2 decimals.
            """
            groups = collections.defaultdict(list)
            for row in self._r:
                groups[row["movieId"]].append(row["rating"])

            scored = {mid: round(metric(vals), 2) for mid, vals in groups.items()}
            top_movies = sorted(scored.items(), key=lambda kv: kv[1], reverse=True)[:n]
            top_movies = {
                self._titles.get(mid, f"Movie {mid}"): val
                for mid, val in top_movies
            }
            return top_movies

        def top_controversial(self, n):  # Топ по дисперсии оценок (разбросу рейтинга) Есть функция variance() не в нампае, но я не помню, встроенная ли она
            """
            The method returns top-n movies by the variance of the ratings.
            It is a dict where the keys are movie titles and the values are the variances.
            Sort it by variance descendingly.
            The values should be rounded to 2 decimals.
            """

            groups = collections.defaultdict(list)
            for row in self._r:
                groups[row["movieId"]].append(row["rating"])

            vars_ = {
                mid: round(variance(vals), 2)
                for mid, vals in groups.items()
                if len(vals) > 1
            }
            top_movies = sorted(vars_.items(), key=lambda kv: kv[1], reverse=True)[:n]
            top_movies = {
                f'id: {mid}, title: {self._titles.get(mid, f"Movie {mid}")}': var for mid, var in top_movies
            }
            return top_movies
        


        # BONUS 1. Распределение оценок ДЛЯ КОНКРЕТНОГО ФИЛЬМА
        def rating_histogram(self, movie_id):
            """
            The method returns a dict where the keys are ratings (float) and
            the values are counts for the selected movieId.
            Sort it by rating ascendingly.
            
            Возвращает dict rating → count (отсортирован ↑ rating).
            """
            rating_histogram = collections.defaultdict(int)
            for row in self._r:
                if row["movieId"] == movie_id:
                    rating_histogram[row["rating"]] += 1
            rating_histogram = dict(sorted(rating_histogram.items()))
            return rating_histogram

        # BONUS 2. Средняя (или медианная) оценка фильма ПО ГОДАМ
        def rating_trend(self, movie_id, metric=average):
            """
            The method returns a dict where the keys are years and
            the values are average / median rating for this movie in that year.
            Sort by year ascendingly.
            Возвращает dict year → average|median rating (↑ year).
            """
            trend_by_year = collections.defaultdict(list)
            for row in self._r:
                if row["movieId"] == movie_id:
                    trend_by_year[row["year"]].append(row["rating"])

            rating_trend = {
                yr: round(metric(vals), 2) for yr, vals in trend_by_year.items()
            }
            rating_trend = dict(sorted(rating_trend.items()))
            return rating_trend


    # ---------------------------- Users -------------------------------
    class Users(Movies):
        """
        
        In this class, three methods should work. 
        The 1st returns the distribution of users by the number of ratings made by them. # Распределение по количеству оценок - словарь
        The 2nd returns the distribution of users by average or median ratings made by them. # Распределение по средней оценке - словарь
        The 3rd returns top-n users with the biggest variance of their ratings. # Топ по разбросу оценок
        Inherit from the class Movies. Several methods are similar to the methods from it.

        Методы аналогичны Movies, но агрегируют по userId.
        """

        def dist_by_num_of_ratings(self):
            per_user = collections.defaultdict(int)
            for row in self._r:
                per_user[row["userId"]] += 1

            distribution = collections.defaultdict(int)
            for _uid, count in per_user.items():
                distribution[count] += 1
            distribution = dict(sorted(distribution.items()))
            return distribution

        def dist_by_rating(self, metric=average):
            per_user = collections.defaultdict(list)
            for row in self._r:
                per_user[row["userId"]].append(row["rating"])

            distribution = collections.defaultdict(int)
            for uid, vals in per_user.items():
                distribution[round(metric(vals), 2)] += 1
            distribution = dict(sorted(distribution.items()))
            return distribution

        def top_controversial(self, n):
            per_user = collections.defaultdict(list)
            for row in self._r:
                per_user[row["userId"]].append(row["rating"])

            vars_ = {
                uid: round(variance(vals), 2)
                for uid, vals in per_user.items()
                if len(vals) > 1
            }
            top_movies = sorted(vars_.items(), key=lambda kv: kv[1], reverse=True)[:n]
            top_movies = {uid: var for uid, var in top_movies}
            return top_movies
        
        # BONUS 3. Топ-N самых активных пользователей (по количеству оценок)
        def top_by_num_of_ratings(self, n):
            """
            The method returns top-n users by the number of ratings.
            It is a dict userId → count, sorted by count descendingly.
            """
            counts = collections.defaultdict(int)
            for row in self._r:
                counts[row["userId"]] += 1

            top_users = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:n]
            top_users = {uid: cnt for uid, cnt in top_users}
            return top_users

        # BONUS 4. Топ-N щедрых пользователей (по средней/медианной оценке)
        def top_generous(self, n, metric=average):
            """
            The method returns top-n users by the average or median rating they give.
            It is a dict userId → score, sorted by score descendingly.
            Values rounded to 2 decimals.
            """
            per_user = collections.defaultdict(list)
            for row in self._r:
                per_user[row["userId"]].append(row["rating"])

            generosity = {
                uid: round(metric(vals), 2) for uid, vals in per_user.items()
            }
            top_users = sorted(generosity.items(), key=lambda kv: kv[1], reverse=True)[:n]
            generous_users = {uid: score for uid, score in top_users}
            return generous_users
        