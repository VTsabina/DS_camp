from movielens_analysis import Links, Ratings, Movies, Tags, median, average
from bs4 import BeautifulSoup
from collections import defaultdict
import pytest
from unittest.mock import patch

# cd test
# python -m pytest test.py

class TestTests:
    #-------------------------Links------------------------
    def test_load_data(self, tmp_path):
        movies_path = tmp_path / "movies.txt"
        movies_path.write_text("movieId,imdbId,tmdbId\n1,0114709,862\n2,0113497,8844\n3,0113228,15602")

        fields_path = tmp_path / "fields.csv"
        fields_path.write_text("movieId,Title,Director,Budget,Cumulative Worldwide Gross,Runtime")

        output_path = tmp_path / "output.txt"
        output_path.touch()  # Создаём пустой файл

        scraper = Links(str(movies_path), str(output_path), str(fields_path))
        assert scraper.data == ["0114709", "0113497", "0113228"]

    def test_load_data_zero(self, tmp_path):
        path = tmp_path / "movies.txt"
        path.write_text(" ")
        scraper = Links(path,"../data/film_info.txt", "../data/list_of_fields.csv")
        assert scraper.data == []

    def test_load_fields(self, tmp_path):
        path = tmp_path / "fields.csv"
        path.write_text("movieId,Title,Director,Budget,Cumulative Worldwide Gross,Runtime")
        scraper = Links("../data/links.txt","../data/film_info.txt", path)
        assert scraper.list_of_fields == ["movieId","Title","Director","Budget","Cumulative Worldwide Gross","Runtime"]

    def test_load_fields_zero(self, tmp_path):
        path = tmp_path / "fields.csv"
        path.write_text(" ")
        scraper = Links("../data/links.txt","../data/film_info.txt", path)
        assert scraper.list_of_fields == [""]

    @pytest.fixture
    def sample_data(self, tmp_path):
        links_txt = tmp_path / "links.txt"
        links_txt.write_text("movieId,imdbId,tmdbId\n1,0114709,862\n2,0113497,8844\n3,0113228,15602")
        
        output_file = tmp_path / "output.txt"
        output_file.touch()
        
        list_of_fields = tmp_path / "list_of_fields.csv"
        list_of_fields.write_text("movieId,Title,Director,Budget,Cumulative Worldwide Gross,Runtime")
        
        scraper = Links(str(links_txt), str(output_file), str(list_of_fields))
        return links_txt, output_file, list_of_fields, scraper

    def test_get_soup_and_extracts_with_mock_html(self, mocker, sample_data):
        with open("../data/test_html_fake.html", 'r', encoding="utf-8") as f:
            fake_html = f.read()

        mock_response = mocker.Mock()
        mock_response.text = fake_html
        mocker.patch("movielens_analysis.requests.get", return_value=mock_response)
        links_txt, output_file, list_of_fields, scraper  = sample_data
        soup = scraper._get_soup("1234567")
        director, title = scraper._extract_metadata(soup)
        budget, worldwide_gross = scraper._extract_financials(soup)
        runtime = scraper._extract_runtime(soup)
        assert isinstance(soup, BeautifulSoup)
        assert director == "Frank Darabont"
        assert title == "The Shawshank Redemption"
        assert budget == 25000000
        assert worldwide_gross == 73300000
        assert runtime == "142"

    def test_get_imdb_with_mock_html(self, mocker, sample_data):
        links_txt, output_file, list_of_fields, scraper = sample_data
        output_file.write_text("")
        with open("../data/test_html_fake.html", 'r', encoding="utf-8") as f:
            fake_html = f.read()
        
        mock_response = mocker.Mock()
        mock_response.text = fake_html
        mocker.patch("movielens_analysis.requests.get", return_value=mock_response)
        imdb_info = scraper.get_imdb()
        assert imdb_info is not None
        assert len(imdb_info) > 0
        
        first_movie = imdb_info[0]
        assert first_movie[0] == '0114709' 
        assert "Frank Darabont" in first_movie
        assert "The Shawshank Redemption" in first_movie
        assert any(str(x) in first_movie for x in [25000000, "25000000"]) 
        assert any(str(x) in first_movie for x in [73300000, "73300000"]) 
        assert "142" in first_movie  # Runtime


    def test_most_profitable(self, mocker, sample_data):
        movies_data = [
            {'title': 'Movie A', 'budget': 100000, 'gross': 500000},
            {'title': 'Movie B', 'budget': 200000, 'gross': 400000},
            {'title': 'Movie C', 'budget': 100000, 'gross': 10000},
            {'title': 'Movie D', 'budget': 150000, 'gross': 150000},
            {'title': 'Movie E', 'budget': 300000, 'gross': 800000},
        ]
        links_txt, output_file, list_of_fields, scraper = sample_data
        mocker.patch.object(scraper, '_read_movie_data', return_value=movies_data)
        top_3 = scraper.most_profitable(3)
        expected = {
            'Movie E': 500000,
            'Movie A': 400000,
            'Movie B': 200000,
        }
        assert top_3 == expected

    def test_less_profitable(self, mocker, sample_data):
        movies_data = [
            {'title': 'Movie A', 'budget': 100000, 'gross': 500000},
            {'title': 'Movie B', 'budget': 200000, 'gross': 400000},
            {'title': 'Movie C', 'budget': 10000, 'gross': 10000},
            {'title': 'Movie D', 'budget': 150000, 'gross': 150000},
            {'title': 'Movie E', 'budget': 300000, 'gross': 800000},
        ]
        links_txt, output_file, list_of_fields, scraper = sample_data
        mocker.patch.object(scraper, '_read_movie_data', return_value=movies_data)
        top_3 = scraper.less_profitable(3)
        expected = {
            'Movie D': 0,
            'Movie C': 0,
            'Movie B': 200000,
        }
        assert top_3 == expected

    def test_top_directors(self, mocker, sample_data):
        movies_data = [
        {'title': 'Movie A', 'director': 'Director X'},
        {'title': 'Movie B', 'director': 'Director Y'},
        {'title': 'Movie C', 'director': 'Director X'},
        {'title': 'Movie D', 'director': 'N/A'},
        {'title': 'Movie E', 'director': 'Director Z'},
    ]
        links_txt, output_file, list_of_fields, scraper = sample_data
        mocker.patch.object(scraper, '_read_movie_data', return_value=movies_data)
        top_3 = scraper.top_directors(3)
        expected = {'Director X': 2, 'Director Y': 1, 'Director Z': 1 }
        assert top_3 == expected

    def test_most_expensive_1(self, mocker, sample_data):
        movies_data = [
        {'title': 'Movie A', 'director': 'Director X', 'budget': 100000, 'gross': 500000},
        {'title': 'Movie B', 'director': 'Director Y', 'budget': 200000, 'gross': 400000},
        {'title': 'Movie C', 'director': 'Director X', 'budget': 50000,  'gross': 100000},
        {'title': 'Movie D', 'director': 'N/A',        'budget': 30000,  'gross': 0},
        {'title': 'Movie E', 'director': 'Director Z', 'budget': 0,      'gross': 0},
    ]
        links_txt, output_file, list_of_fields, scraper = sample_data
        mocker.patch.object(scraper, '_read_movie_data', return_value=movies_data)
        top_3 = scraper.most_expensive(3)
        expected = {'Movie B': 200000, 'Movie A': 100000, 'Movie C': 50000}
        assert top_3 == expected

    def test_the_cheapest(self, mocker, sample_data):
        movies_data = [
        {'title': 'Movie A', 'director': 'Director X', 'budget': 100000, 'gross': 500000},
        {'title': 'Movie B', 'director': 'Director Y', 'budget': 200000, 'gross': 400000},
        {'title': 'Movie C', 'director': 'Director X', 'budget': 50000,  'gross': 100000},
        {'title': 'Movie D', 'director': 'N/A',        'budget': 30000,  'gross': 0},
        {'title': 'Movie E', 'director': 'Director Z', 'budget': 0,      'gross': 0},
    ]
        links_txt, output_file, list_of_fields, scraper = sample_data
        mocker.patch.object(scraper, '_read_movie_data', return_value=movies_data)
        top_3 = scraper.the_cheapest(3)
        expected = {'Movie E': 0, 'Movie D': 30000, 'Movie C': 50000}
        assert top_3 == expected

    def test_longest_1(self, mocker, sample_data):
        movies_data = [
            {'title': 'Movie A', 'runtime': 120},
            {'title': 'Movie B', 'runtime': 90},
            {'title': 'Movie C', 'runtime': 110},
            {'title': 'Movie D', 'runtime': 100},
            {'title': 'Movie E', 'runtime': 80},
        ]
        links_txt, output_file, list_of_fields, scraper = sample_data
        mocker.patch.object(scraper, '_read_movie_data', return_value=movies_data)
        top_3 = scraper.longest(3)
        expected = {'Movie A': 120, 'Movie C': 110, 'Movie D': 100}
        assert top_3 == expected

    def test_shortest(self, mocker, sample_data):
        movies_data = [
            {'title': 'Movie A', 'runtime': 120},
            {'title': 'Movie B', 'runtime': 90},
            {'title': 'Movie C', 'runtime': 110},
            {'title': 'Movie D', 'runtime': 100},
            {'title': 'Movie E', 'runtime': 80},
        ]
        links_txt, output_file, list_of_fields, scraper = sample_data
        mocker.patch.object(scraper, '_read_movie_data', return_value=movies_data)
        top_3 = scraper.shortest(3)
        expected = {'Movie E': 80, 'Movie B': 90, 'Movie D': 100}
        assert top_3 == expected

    def test_top_cost_per_minute(self, mocker, sample_data):
        movies_data = [
        {'title': 'Movie A', 'director': 'Director X', 'budget': 100000, 'gross': 500000, 'runtime': 120},
        {'title': 'Movie B', 'director': 'Director Y', 'budget': 200000, 'gross': 400000, 'runtime': 90},
        {'title': 'Movie C', 'director': 'Director X', 'budget': 50000,  'gross': 100000, 'runtime': 110},
        {'title': 'Movie D', 'director': 'N/A',        'budget': 30000,  'gross': 0,      'runtime': 100},
        {'title': 'Movie E', 'director': 'Director Z', 'budget': 0,      'gross': 0,      'runtime': 80},
    ]
        links_txt, output_file, list_of_fields, scraper = sample_data
        mocker.patch.object(scraper, '_read_movie_data', return_value=movies_data)
        top_2 = scraper.top_cost_per_minute(2)
        expected = {'Movie B': 2222.22, 'Movie A': 833.33}
        assert top_2 == expected

    def test_less_cost_per_minute(self, mocker, sample_data):
        movies_data = [
        {'title': 'Movie A', 'director': 'Director X', 'budget': 100000, 'gross': 500000, 'runtime': 120},
        {'title': 'Movie B', 'director': 'Director Y', 'budget': 200000, 'gross': 400000, 'runtime': 90},
        {'title': 'Movie C', 'director': 'Director X', 'budget': 50000,  'gross': 100000, 'runtime': 110},
        {'title': 'Movie D', 'director': 'N/A',        'budget': 30000,  'gross': 0,      'runtime': 100},
        {'title': 'Movie E', 'director': 'Director Z', 'budget': 0,      'gross': 0,      'runtime': 80},
    ]
        links_txt, output_file, list_of_fields, scraper = sample_data
        mocker.patch.object(scraper, '_read_movie_data', return_value=movies_data)
        top_2 = scraper.less_cost_per_minute(2)
        expected = {'Movie D': 300.0, 'Movie C': 454.55}
        assert top_2 == expected

    def test_top_longest_title(self, mocker, sample_data):
        movies_data = [
            {'title': 'A', 'runtime': 120},
            {'title': 'AB', 'runtime': 90},
            {'title': 'ABC', 'runtime': 110},
            {'title': 'ABCD', 'runtime': 100},
            {'title': 'ABCDE', 'runtime': 80},
        ]
        links_txt, output_file, list_of_fields, scraper = sample_data
        mocker.patch.object(scraper, '_read_movie_data', return_value=movies_data)
        top_3 = scraper.top_longest_title(3)
        expected = ['ABCDE', 'ABCD', 'ABC']
        assert top_3 == expected

    def test_top_shortest_title(self, mocker, sample_data):
        movies_data = [
            {'title': 'A', 'runtime': 120},
            {'title': 'AB', 'runtime': 90},
            {'title': 'ABC', 'runtime': 110},
            {'title': 'ABCD', 'runtime': 100},
            {'title': 'ABCDE', 'runtime': 80},
        ]
        links_txt, output_file, list_of_fields, scraper = sample_data
        mocker.patch.object(scraper, '_read_movie_data', return_value=movies_data)
        top_3 = scraper.top_shortest_title(3)
        expected = ['A', 'AB', 'ABC']
        assert top_3 == expected
    
    #-------------------------Ratings-----------------------
    @pytest.fixture
    def tiny_csv(self, tmp_path):
        csv_path = tmp_path / "ratings.csv"
        movies_path = tmp_path / "movies.csv"

        # 3 фильма
        movies_path.write_text(
            "movieId,title,genres\n"
            "1,Film A (2000),Drama\n"
            "2,Film B (2001),Action\n"
            "3,Film C (2002),Comedy\n"
        )

        csv_path.write_text(
            "userId,movieId,rating,timestamp\n"
            # user 10: щедрый
            "10,1,5.0,946684800\n"     # 2000-01-01
            "10,2,4.5,978307200\n"     # 2001-01-01
            # user 20: троечник
            "20,1,3.0,946684800\n"
            "20,3,3.0,1009843200\n"    # 2002-01-01
            # user 30: хаотик
            "30,1,1.0,946684800\n"
            "30,1,5.0,978307200\n"
            "30,2,2.0,978307200\n"
        )
        return csv_path


    # ------- Movies -------
    def test_dist_by_year(self, tiny_csv):
        r = Ratings(tiny_csv)
        movies = r.Movies(r)
        assert movies.dist_by_year() == {2000: 3, 2001: 3, 2002: 1}

    def test_dist_by_rating(self, tiny_csv):
        r = Ratings(tiny_csv)
        movies = r.Movies(r)
        expected = {1.0: 1, 2.0: 1, 3.0: 2, 4.5: 1, 5.0: 2}
        assert movies.dist_by_rating() == expected

    def test_top_by_num_of_ratings(self, tiny_csv):
        r = Ratings(tiny_csv)
        movies = r.Movies(r)
        top_1 = movies.top_by_num_of_ratings(1)
        assert list(top_1.values())[0] == 4

    def test_top_by_ratings_average(self, tiny_csv):
        r = Ratings(tiny_csv)
        movies = r.Movies(r)
        res = movies.top_by_ratings(1, metric=average)
        assert list(res.values())[0] == 3.5

    def test_top_controversial(self, tiny_csv):
        r = Ratings(tiny_csv)
        movies = r.Movies(r)
        res = movies.top_controversial(1)
        assert list(res.values())[0] == pytest.approx(2.75, abs=0.01)

    def test_rating_histogram(self, tiny_csv):
        r = Ratings(tiny_csv)
        movies = r.Movies(r)
        expected = {1.0: 1, 3.0: 1, 5.0: 2}    # Film A
        assert movies.rating_histogram(1) == expected

    def test_rating_trend_median(self, tiny_csv):
        r = Ratings(tiny_csv)
        movies = r.Movies(r)
        expected = {2000: 3.0, 2001: 5.0}      # Film A
        assert movies.rating_trend(1, metric=median) == expected


    # ------- Тесты класса Users -------─
    def test_dist_by_num_of_ratings_users(self, tiny_csv):
        r = Ratings(tiny_csv)
        users = r.Users(r)
        expected = {2: 2, 3: 1}
        assert users.dist_by_num_of_ratings() == expected

    def test_dist_by_rating_users(self, tiny_csv):
        r = Ratings(tiny_csv)
        users = r.Users(r)
        expected = {2.67: 1, 3.0: 1, 4.75: 1}
        assert users.dist_by_rating(metric=average) == expected

    def test_top_controversial_users(self, tiny_csv):
        r = Ratings(tiny_csv)
        users = r.Users(r)
        res = users.top_controversial(1)
        assert list(res.values())[0] == pytest.approx(2.89, abs=0.01)

    def test_top_by_num_of_ratings_users(self, tiny_csv):
        r = Ratings(tiny_csv)
        users = r.Users(r)
        top = users.top_by_num_of_ratings(1)
        assert list(top.values())[0] == 3   # user 30

    def test_top_generous_users(self, tiny_csv):
        r = Ratings(tiny_csv)
        users = r.Users(r)
        generous = users.top_generous(2, metric=average)
        expected_first_score = 4.75   # user 10
        assert list(generous.values())[0] == expected_first_score
    
    #-------------------------Movies------------------------
    @pytest.fixture
    def movie_instance(self):
        path = '../../datasets/movies.csv'
        instance = Movies(path)
        return instance

    def test_dist_by_release(self, movie_instance):
        result = movie_instance.dist_by_release()
        assert result == {2002: 311, 2006: 295, 2001: 294, 2007: 284, 2000: 283, 2009: 282, 2003: 279, 2004: 279, 2014: 278, 
                        1996: 276, 2015: 274, 2005: 273, 2008: 269, 1999: 263, 1997: 260, 1995: 259, 1998: 258, 2011: 254, 
                        2010: 247, 2013: 239, 1994: 237, 2012: 233, 2016: 218, 1993: 198, 1992: 167, 1988: 165, 1987: 153, 
                        1990: 147, 1991: 147, 2017: 147, 1989: 142, 1986: 139, 1985: 126, 1984: 101, 1981: 92, 1980: 89, 
                        1982: 87, 1983: 83, 1979: 69, 1977: 63, 1973: 59, 1978: 59, 1965: 47, 1971: 47, 1974: 45, 1976: 44, 
                        1964: 43, 1967: 42, 1968: 42, 1975: 42, 1966: 42, 2018: 41, 1962: 40, 1972: 39, 1963: 39, 1959: 37, 
                        1960: 37, 1955: 36, 1969: 35, 1961: 34, 1970: 33, 1957: 33, 1958: 31, 1953: 30, 1956: 30, 1940: 25, 
                        1949: 25, 1954: 23, 1942: 23, 1939: 23, 1946: 23, 1951: 22, 1950: 21, 1947: 20, 1948: 20, 1941: 18, 
                        1936: 18, 1945: 17, 1937: 16, 1952: 16, 1944: 16, 1938: 15, 1931: 14, 1935: 13, 0: 13, 1933: 12, 
                        1934: 11, 1943: 10, 1932: 9, 1927: 7, 1930: 5, 1926: 5, 1924: 5, 1929: 4, 1928: 4, 1925: 4, 1923: 4, 
                        1916: 4, 1920: 2, 1922: 1, 1919: 1, 1921: 1, 1915: 1, 1917: 1, 1902: 1, 1903: 1, 1908: 1}

    def test_dist_by_genres(self, movie_instance):
        result = movie_instance.dist_by_genres()
        assert result == {'Drama': 4361, 'Comedy': 3756, 'Thriller': 1894, 'Action': 1828, 'Romance': 1596, 
                        'Adventure': 1263, 'Crime': 1199, 'Sci-Fi': 980, 'Horror': 978, 'Fantasy': 779, 
                        'Children': 664, 'Animation': 611, 'Mystery': 573, 'Documentary': 440, 'War': 382, 
                        'Musical': 334, 'Western': 167, 'IMAX': 158, 'Film-Noir': 87, '(no genres listed)': 34}

    def test_most_genres(self, movie_instance):
        result = movie_instance.most_genres(10)
        assert isinstance(result, dict)
        assert len(result) == 10
        assert result == {'Rubber (2010)': 10, 'Patlabor: The Movie (Kidô keisatsu patorebâ: The Movie) (1989)': 8, 
                        'Mulan (1998)': 7, 'Who Framed Roger Rabbit? (1988)': 7, 'Osmosis Jones (2001)': 7, 
                        'Interstate 60 (2002)': 7, 'Robots (2005)': 7, 'Pulse (2006)': 7, 
                        'Aqua Teen Hunger Force Colon Movie Film for Theaters (2007)': 7, 'Enchanted (2007)': 7}
        
    def test_most_genres_no_num(self, movie_instance):
        result = movie_instance.most_genres(0)
        assert result == {}

    def test_most_genres_min(self, movie_instance):
        result = movie_instance.most_genres(-2)
        assert result == {}

    def test_genre_filter(self, movie_instance):
        filtered_titles = movie_instance.genre_filter(['Comedy', 'Horror', 'Drama'])
        assert filtered_titles == ['Surf Nazis Must Die (1987)', 'Visitor Q (Bizita Q) (2001)', 'Ichi the Killer (Koroshiya 1) (2001)', 
                                'Gozu (Gokudô kyôfu dai-gekijô: Gozu) (2003)', "Pusher III: I'm the Angel of Death (2005)", 
                                'Host, The (Gwoemul) (2006)', 'Ex Drummer (2007)', 'Hood of Horror (2006)', 'Rubber (2010)', 
                                'Tusk (2014)', 'Buzzard (2015)', 'He Never Died (2015)']
        
    def test_genre_filter_empty_list(self, movie_instance):
        filtered_titles = movie_instance.genre_filter([])
        assert filtered_titles == []

    def test_genre_correlation(self, movie_instance):
        result = movie_instance.genre_correlation('Comedy', 5)
        assert isinstance(result, dict)
        assert result == {'Comedy': {'Drama': 1013, 'Romance': 884, 'Action': 429, 'Adventure': 399, 'Children': 362}}

    def test_genre_correlation_no_genre(self, movie_instance):
        result = movie_instance.genre_correlation('', 5)
        assert isinstance(result, dict)
        assert result == {'': {}}

    def test_genre_correlation_no_num(self, movie_instance):
        result = movie_instance.genre_correlation('Comedy', 0)
        assert isinstance(result, dict)
        assert result == {}

    def test_genre_frequency_by_year(self, movie_instance):
        result = movie_instance.genre_frequency_by_year(2)
        assert isinstance(result, dict)
        assert result == {1995: {'Drama': 123, 'Comedy': 91}, 1994: {'Drama': 114, 'Comedy': 111}, 1996: {'Drama': 128, 'Comedy': 108}, 
                        1976: {'Drama': 21, 'Comedy': 16}, 1992: {'Drama': 78, 'Comedy': 69}, 1967: {'Drama': 23, 'Comedy': 14}, 
                        1993: {'Drama': 99, 'Comedy': 77}, 1964: {'Drama': 17, 'Comedy': 17}, 1977: {'Drama': 27, 'Comedy': 21}, 
                        1965: {'Drama': 24, 'Comedy': 17}, 1982: {'Comedy': 32, 'Drama': 29}, 1990: {'Drama': 62, 'Comedy': 59}, 
                        1991: {'Comedy': 69, 'Drama': 63}, 1989: {'Comedy': 71, 'Drama': 60}, 1937: {'Drama': 12, 'Romance': 4}, 
                        1940: {'Drama': 14, 'Comedy': 11}, 1969: {'Drama': 17, 'Comedy': 11}, 1981: {'Comedy': 32, 'Drama': 31}, 
                        1973: {'Drama': 29, 'Crime': 17}, 1970: {'Drama': 18, 'Comedy': 10}, 1955: {'Drama': 21, 'Crime': 8}, 
                        1959: {'Drama': 15, 'War': 8}, 1968: {'Drama': 17, 'Comedy': 13}, 1988: {'Comedy': 72, 'Drama': 67}, 
                        1997: {'Drama': 125, 'Comedy': 94}, 1972: {'Drama': 22, 'Comedy': 15}, 1943: {'Drama': 8, 'Crime': 2}, 
                        1952: {'Drama': 9, 'Comedy': 7}, 1951: {'Drama': 12, 'Romance': 7}, 1957: {'Drama': 18, 'Comedy': 8}, 
                        1961: {'Drama': 18, 'Comedy': 12}, 1958: {'Drama': 11, 'Comedy': 10}, 1954: {'Drama': 15, 'Thriller': 4}, 
                        1934: {'Comedy': 6, 'Drama': 4}, 1944: {'Drama': 11, 'Romance': 5}, 1960: {'Drama': 19, 'Horror': 8}, 
                        1963: {'Comedy': 15, 'Drama': 15}, 1942: {'Drama': 13, 'Romance': 10}, 1941: {'Drama': 9, 'Comedy': 8}, 
                        1953: {'Drama': 17, 'Comedy': 9}, 1939: {'Drama': 15, 'Romance': 9}, 1950: {'Drama': 10, 'Romance': 9}, 
                        1946: {'Drama': 14, 'Film-Noir': 8}, 1945: {'Drama': 7, 'Mystery': 6}, 1938: {'Drama': 9, 'Comedy': 8}, 
                        1947: {'Drama': 12, 'Comedy': 9}, 1935: {'Comedy': 7, 'Romance': 6}, 1936: {'Romance': 10, 'Comedy': 7}, 
                        1956: {'Drama': 18, 'Sci-Fi': 6}, 1949: {'Drama': 15, 'Comedy': 8}, 1932: {'Romance': 4, 'Drama': 4}, 
                        1975: {'Drama': 19, 'Comedy': 12}, 1974: {'Drama': 20, 'Comedy': 13}, 1971: {'Drama': 20, 'Action': 17}, 
                        1979: {'Drama': 32, 'Comedy': 24}, 1987: {'Comedy': 77, 'Drama': 56}, 1986: {'Drama': 55, 'Comedy': 54}, 
                        1980: {'Drama': 32, 'Comedy': 29}, 1978: {'Comedy': 19, 'Drama': 17}, 1985: {'Comedy': 54, 'Drama': 45}, 
                        1966: {'Comedy': 19, 'Drama': 18}, 1962: {'Drama': 24, 'Adventure': 7}, 1983: {'Comedy': 31, 'Drama': 29}, 
                        1984: {'Comedy': 40, 'Drama': 35}, 1948: {'Drama': 15, 'Adventure': 4}, 1933: {'Comedy': 5, 'Musical': 4}, 
                        1931: {'Drama': 9, 'Comedy': 4}, 1922: {'Horror': 1}, 1998: {'Drama': 122, 'Comedy': 99}, 1929: {'Musical': 2, 'Documentary': 1}, 
                        1930: {'Drama': 4, 'Action': 1}, 1927: {'Drama': 5, 'Romance': 2}, 1928: {'Comedy': 3, 'Animation': 1}, 
                        1999: {'Drama': 124, 'Comedy': 113}, 2000: {'Drama': 138, 'Comedy': 117}, 1926: {'Drama': 3, 'Comedy': 2}, 
                        1919: {'Comedy': 1, 'Drama': 1}, 1921: {'Comedy': 1, 'Drama': 1}, 1925: {'Adventure': 2, 'Comedy': 2}, 
                        1923: {'Drama': 2, 'Comedy': 2}, 2001: {'Drama': 148, 'Comedy': 127}, 2002: {'Drama': 150, 'Comedy': 116}, 
                        2003: {'Drama': 129, 'Comedy': 109}, 1920: {'Crime': 1, 'Fantasy': 1}, 1915: {'Drama': 1, 'War': 1}, 
                        1924: {'Fantasy': 3, 'Comedy': 2}, 2004: {'Drama': 128, 'Comedy': 111}, 1916: {'Drama': 1, 'Action': 1}, 
                        1917: {'Comedy': 1}, 2005: {'Drama': 140, 'Comedy': 120}, 2006: {'Drama': 146, 'Comedy': 118}, 1902: {'Action': 1, 'Adventure': 1}, 
                        0: {'(no genres listed)': 9, 'Sci-Fi': 2}, 1903: {'Crime': 1, 'Western': 1}, 2007: {'Drama': 142, 'Comedy': 102}, 
                        2008: {'Drama': 113, 'Comedy': 104}, 2009: {'Drama': 131, 'Comedy': 111}, 2010: {'Drama': 102, 'Comedy': 97}, 
                        2011: {'Drama': 110, 'Comedy': 101}, 2012: {'Comedy': 103, 'Drama': 92}, 2013: {'Drama': 98, 'Comedy': 89}, 
                        2014: {'Drama': 117, 'Comedy': 116}, 2015: {'Comedy': 104, 'Drama': 101}, 2016: {'Comedy': 75, 'Drama': 69}, 
                        2017: {'Comedy': 56, 'Drama': 45}, 2018: {'Comedy': 17, 'Action': 16}, 1908: {'Animation': 1, 'Comedy': 1}}
        
    def test_genre_frequency_by_year_no_num(self, movie_instance):
        result = movie_instance.genre_frequency_by_year(0)
        assert isinstance(result, dict)
        assert result == {}

    def test_genre_frequency_by_year_minus(self, movie_instance):
        result = movie_instance.genre_frequency_by_year(-4)
        assert isinstance(result, dict)
        assert result == {}

    def test_definite_genre_frequency_by_year(self, movie_instance):
        result = movie_instance.definite_genre_frequency_by_year('Comedy')
        assert isinstance(result, dict)
        assert result == {'Comedy': {2001: 127, 2005: 120, 2006: 118, 2000: 117, 2002: 116, 2014: 116, 1999: 113, 1994: 111, 2004: 111, 
                                    2009: 111, 2003: 109, 1996: 108, 2008: 104, 2015: 104, 2012: 103, 2007: 102, 2011: 101, 1998: 99, 
                                    2010: 97, 1997: 94, 1995: 91, 2013: 89, 1993: 77, 1987: 77, 2016: 75, 1988: 72, 1989: 71, 1992: 69, 
                                    1991: 69, 1990: 59, 2017: 56, 1985: 54, 1986: 54, 1984: 40, 1982: 32, 1981: 32, 1983: 31, 1980: 29, 
                                    1979: 24, 1977: 21, 1978: 19, 1966: 19, 1964: 17, 1965: 17, 2018: 17, 1976: 16, 1963: 15, 1972: 15, 
                                    1967: 14, 1973: 13, 1968: 13, 1974: 13, 1975: 12, 1961: 12, 1971: 12, 1940: 11, 1969: 11, 1958: 10, 
                                    1970: 10, 1953: 9, 1939: 9, 1942: 9, 1947: 9, 1957: 8, 1938: 8, 1941: 8, 1955: 8, 1949: 8, 1952: 7, 
                                    1960: 7, 1959: 7, 1935: 7, 1936: 7, 1962: 7, 1934: 6, 1950: 6, 1951: 5, 1933: 5, 1956: 4, 1944: 4, 
                                    1931: 4, 1954: 3, 1937: 3, 1928: 3, 1932: 3, 1948: 3, 1926: 2, 1945: 2, 1925: 2, 1924: 2, 1923: 2, 
                                    1919: 1, 1921: 1, 1946: 1, 1930: 1, 1927: 1, 1917: 1, 1929: 1, 1920: 1, 1916: 1, 1908: 1}}

    def test_definite_genre_frequency_by_year_no_genre(self, movie_instance):
        result = movie_instance.definite_genre_frequency_by_year('')
        assert isinstance(result, dict)
        assert result == {'': {}}
    
    #-------------------------Tags------------------------
    @pytest.fixture
    def tags_instance(self):
        instance = Tags('../../datasets/tags.csv')
        return instance

    def test_most_words(self, tags_instance):
        result = tags_instance.most_words(5)
        assert isinstance(result, dict)
        assert result == {'Something For Everyone In This One... Saw It Without And Plan On Seeing It With Kids!': 16, 
                        'The Catholic Church Is The Most Corrupt Organization In History': 10, 
                        'Villain Nonexistent Or Not Needed For Good Story': 8, '06 Oscar Nominated Best Movie - Animation': 7, 
                        'It Was Melodramatic And Kind Of Dumb': 7}
        
    def test_most_words_no_num(self, tags_instance):
        result = tags_instance.most_words(0)
        assert isinstance(result, dict)
        assert result == {}

    def test_most_words_min(self, tags_instance):
        result = tags_instance.most_words(-1)
        assert isinstance(result, dict)
        assert result == {}

    def test_longest(self, tags_instance):
        result = tags_instance.longest(5)
        assert all(isinstance(tag_str, str) for tag_str in result)
        assert result == ['Something For Everyone In This One... Saw It Without And Plan On Seeing It With Kids!', 
                        'The Catholic Church Is The Most Corrupt Organization In History', 
                        'Villain Nonexistent Or Not Needed For Good Story', 
                        'R:Disturbing Violent Content Including Rape', 
                        '06 Oscar Nominated Best Movie - Animation']
        
    def test_longest_no_num(self, tags_instance):
        result = tags_instance.longest(0)
        assert all(isinstance(tag_str, str) for tag_str in result)
        assert result == []

    def test_longest_min(self, tags_instance):
        result = tags_instance.longest(-3)
        assert all(isinstance(tag_str, str) for tag_str in result)
        assert result == []

    def test_most_words_and_longest(self, tags_instance):
        result = tags_instance.most_words_and_longest(10)
        assert isinstance(result, list)
        assert result == ['06 Oscar Nominated Best Movie - Animation', 'It Was Melodramatic And Kind Of Dumb', 'Oscar (Best Effects - Visual Effects)', 
                        'Something For Everyone In This One... Saw It Without And Plan On Seeing It With Kids!', 
                        'Stop Using Useless Characters For Filler', 'The Catholic Church Is The Most Corrupt Organization In History', 
                        'Villain Nonexistent Or Not Needed For Good Story']

    def test_most_words_and_longest_no_num(self, tags_instance):
        result = tags_instance.most_words_and_longest(0)
        assert isinstance(result, list)
        assert result == []

    def test_most_words_and_longest_min(self, tags_instance):
        result = tags_instance.most_words_and_longest(-2)
        assert isinstance(result, list)
        assert result == []

    def test_most_popular(self, tags_instance):
        result = tags_instance.most_popular(10)
        assert isinstance(result, dict)
        assert result == {'In Netflix Queue': 131, 'Atmospheric': 41, 'Funny': 24, 'Superhero': 24, 'Surreal': 24, 
                        'Thought-Provoking': 24, 'Sci-Fi': 23, 'Disney': 23, 'Quirky': 22, 'Religion': 22}
        
    def test_most_popular_no_num(self, tags_instance):
        result = tags_instance.most_popular(0)
        assert isinstance(result, dict)
        assert result == {}

    def test_most_popular_min(self, tags_instance):
        result = tags_instance.most_popular(-3)
        assert isinstance(result, dict)
        assert result == {}
        
    def test_tags_with(self, tags_instance):
        results = tags_instance.tags_with('and')
        for tag in results:
            assert "and".title() in tag
            assert results == ['Astaire And Rogers', 'Black And White', 'Day And Hudson', 'Good And Evil', 'Hepburn And Tracy', 
                            'It Was Melodramatic And Kind Of Dumb', 'Jay And Silent Bob', 'Jekyll And Hyde', 'Nick And Nora Charles', 
                            'Robots And Androids', 'Rogers And Hammerstein', 'Simon And Garfunkel', 
                            'Something For Everyone In This One... Saw It Without And Plan On Seeing It With Kids!']
        
    def test_tags_with_no_word(self, tags_instance):
        results = tags_instance.tags_with('')
        assert results == []

    def test_most_popular_by_year(self, tags_instance):
        results = tags_instance.most_popular_by_year(2010, 5)
        assert isinstance(results, dict)
        assert results == {'Sci-Fi': 5, 'Dark Comedy': 3, 'Sequel': 3, 'Bad Plot': 3, 'Based On A Book': 2}

    def test_most_popular_by_year_wrong_year(self, tags_instance):
        results = tags_instance.most_popular_by_year(0, 5)
        assert isinstance(results, dict)
        assert results == {}

    def test_most_popular_by_year_no_num(self, tags_instance):
        results = tags_instance.most_popular_by_year(2010, 0)
        assert isinstance(results, dict)
        assert results == {}

    def test_tags_for_years(self, tags_instance):
        results = tags_instance.tags_for_years()
        assert isinstance(results, dict)
        assert results == {2006: 1533, 2018: 844, 2016: 355, 2017: 329, 2015: 191, 2009: 166, 
                            2010: 133, 2012: 47, 2007: 46, 2011: 13, 2013: 10, 2008: 9, 2014: 7}
    
    def test_count_definite_by_year(self, tags_instance):
        tags = ['atmospheric', 'funny', 'superhero']
        results = tags_instance.count_definite_by_year(tags)
        assert isinstance(results, dict)
        assert results == {'Atmospheric': {2018: 23, 2015: 2, 2011: 1, 2012: 1, 2016: 6, 2010: 1, 2009: 4, 2017: 3}, 
                            'Funny': {2015: 4, 2018: 15, 2012: 1, 2016: 1, 2010: 1, 2017: 2}, 
                            'Superhero': {2018: 7, 2006: 14, 2012: 1, 2013: 1, 2015: 1}}
    
    def test_count_definite_by_year_empty_list(self, tags_instance):
        tags = []
        results = tags_instance.count_definite_by_year(tags)
        assert isinstance(results, dict)
        assert results == {}

    def test_tag_count_by_distinct_users(self, tags_instance):
        results = tags_instance.tag_count_by_distinct_users(20)
        assert isinstance(results, dict)
        assert results == {'Funny': 10, 'Sci-Fi': 10, 'Atmospheric': 10, 'Dark Comedy': 9, 'Comedy': 9, 'Music': 8, 'Mindfuck': 8, 
                            'Suspense': 8, 'Twist Ending': 7, 'Animation': 7, 'Superhero': 7, 'Action': 7, 'Psychology': 7, 
                            'Thought-Provoking': 7, 'Drugs': 6, 'Black Comedy': 6, 'Classic': 6, 'Comic Book': 6, 'Adventure': 6, 'Visually Appealing': 6}
    
    def test_tag_count_by_distinct_users_no_num(self, tags_instance):
        results = tags_instance.tag_count_by_distinct_users(0)
        assert isinstance(results, dict)
        assert results == {}

    def test_tag_count_by_distinct_users_minus(self, tags_instance):
        results = tags_instance.tag_count_by_distinct_users(-5)
        assert isinstance(results, dict)
        assert results == {}

    def test_distinct_tag_count_by_distinct_users(self, tags_instance):
        results = tags_instance.distinct_tag_count_by_distinct_users('Funny')
        assert results == 10
    
    def test_distinct_tag_count_by_distinct_users_wrong(self, tags_instance):
        results = tags_instance.distinct_tag_count_by_distinct_users('HHH')
        assert results == 0

    def test_tag_count_by_distinct_movies(self, tags_instance):
        results = tags_instance.tag_count_by_distinct_movies(20)
        assert isinstance(results, dict)
        assert results == {'In Netflix Queue': 131, 'Atmospheric': 37, 'Funny': 22, 'Quirky': 22, 'Disney': 22, 'Superhero': 22, 
                            'Surreal': 22, 'Religion': 22, 'Sci-Fi': 19, 'Comedy': 19, 'Politics': 19, 'Suspense': 19, 'Psychology': 19, 
                            'Thought-Provoking': 19, 'Crime': 19, 'Visually Appealing': 18, 'Twist Ending': 16, 'Dark Comedy': 16, 'Dark': 16, 'Action': 16}

    def test_tag_count_by_distinct_movies_no_num(self, tags_instance):
        results = tags_instance.tag_count_by_distinct_movies(0)
        assert isinstance(results, dict)
        assert results == {}

    def test_tag_count_by_distinct_movies_minus(self, tags_instance):
        results = tags_instance.tag_count_by_distinct_movies(-4)
        assert isinstance(results, dict)
        assert results == {}