# summarizer.py - Movie/Drama Story Summarizer 
import nltk

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)
    nltk.download('punkt', quiet=True)

import wikipedia
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import re


def get_summary(title):
    """Fetch story-focused plot summary and genre from Wikipedia."""
    try:
        wikipedia.set_lang("en")
        # Try exact title first
        try:
            page = wikipedia.page(title, auto_suggest=False)
            return process_page(page, title)
        except wikipedia.exceptions.PageError:
            pass

        # Smart search
        search_term = title
        if any(x in title.lower() for x in ["queen", "game"]):
            search_term += " (TV series)"
        else:
            search_term += " (film)"

        search_results = wikipedia.search(search_term, results=5)
        if not search_results:
            return {'error': f'No results for "{title}". Try a different spelling.'}

        # Pick best match
        page_title = search_results[0]  # Top result
        page = wikipedia.page(page_title, auto_suggest=False)
        return process_page(page, page_title)

    except wikipedia.exceptions.DisambiguationError as e:
        options = ', '.join(e.options[:3])
        return {'error': f'Ambiguous title. Suggestions: {options}. Try one of those.'}
    except wikipedia.exceptions.PageError:
        return {'error': f'Page not found for "{title}". Check spelling or try "{title} (film)".'}
    except Exception as e:
        return {'error': f'Error: {str(e)}'}


def process_page(page, page_title):
    """Process page for summary, genre, year."""
    full_page = page.content

    # Extract plot section (try Plot or Synopsis)
    plot_match = re.search(r'==\s*(Plot|Synopsis|Story)\s*==\n([\s\S]*?)(?=\n==|$)', full_page, re.IGNORECASE)
    full_text = plot_match.group(2).strip() if plot_match else page.summary
    # Clean wiki markup
    full_text = re.sub(r'\[\[.*?\]\]|\{\{.*?\}\}|<.*?>', '', full_text).strip()

    # Extract year
    year_match = re.search(r'\b(19|20)\d{2}\b', full_page)
    year = year_match.group(0) if year_match else "Unknown"

    # Extract genre from infobox
    genre = "Unknown"
    genre_match = re.search(r'\|genres?\s*=\s*({{.*?}}|[^\n|]+?)(?=\n\| |\n}}|$)', full_page, re.IGNORECASE)
    if genre_match:
        genre = genre_match.group(1).strip()
        genre = re.sub(r'\[\[|\]\]|\{\{.*?\}\}|\|', ', ', genre).strip()
        genre = re.sub(r'\s*,\s*', ', ', genre).strip(', ')
    if not genre or genre == "Unknown":
        # Keyword fallback
        lower_text = full_page.lower()
        genres = []
        for g in [("comedy", "Comedy"), ("humour", "Comedy"), ("humorous", "Comedy"),
                  ("drama", "Drama"), ("melodrama", "Drama"), ("romance", "Romance"),
                  ("romantic", "Romance"), ("horror", "Horror"), ("supernatural", "Horror"),
                  ("sci-fi", "Sci-Fi"), ("science fiction", "Sci-Fi"), ("thriller", "Thriller"),
                  ("suspense", "Thriller"), ("fantasy", "Fantasy"), ("historical", "Historical"),
                  ("period drama", "Historical"), ("action", "Action"), ("adventure", "Action"),
                  ("mystery", "Mystery"), ("crime", "Crime")]:
            if g[0] in lower_text and g[1] not in genres:
                genres.append(g[1])
        genre = ", ".join(genres) if genres else "Unknown"

    # Summarize to 1-3 sentences
    parser = PlaintextParser.from_string(full_text[:2000], Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary_sentences = summarizer(parser.document, 3)
    concise_summary = ' '.join(str(s) for s in summary_sentences).strip()

    return {
        'title': page_title,
        'summary': concise_summary,
        'year': year,
        'genre': genre
    }

if __name__ == "__main__":
    print("Enter movie/drama title (or 'quit' to exit):")
    while True:
        title = input("> ").strip()
        if title.lower() == 'quit':
            break
        result = get_summary(title)
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"\nTitle: {result['title']}")
            print(f"Genre: {result['genre']}, Year: {result['year']}")
            print(f"Summary: {result['summary']}\n")
