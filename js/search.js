/**
 * Client-side search using lunr.js
 */

(function() {
  'use strict';

  let searchIndex = null;
  let searchData = [];

  // Initialize search when DOM is ready
  document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    if (!searchInput || !searchResults) {
      return; // Not on search page
    }

    // Load search index
    loadSearchIndex();

    // Set up search input handler
    let debounceTimer;
    searchInput.addEventListener('input', function() {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function() {
        performSearch(searchInput.value, searchResults);
      }, 300); // Debounce for 300ms
    });

    // Perform search if there's a query parameter
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q');
    if (query) {
      searchInput.value = query;
      performSearch(query, searchResults);
    }
  });

  /**
   * Load the search index and data
   */
  function loadSearchIndex() {
    searchResults.innerHTML = '<div class="search-loading">Loading search index...</div>';

    // Fetch search data from Jekyll-generated JSON
    fetch('/search-data.json')
      .then(response => response.json())
      .then(data => {
        searchData = data;

        // Build lunr index
        searchIndex = lunr(function() {
          this.ref('id');
          this.field('title', { boost: 10 });
          this.field('content');
          this.field('tags', { boost: 5 });
          this.field('excerpt');

          data.forEach(function(doc, idx) {
            doc.id = idx;
            this.add(doc);
          }, this);
        });

        searchResults.innerHTML = '<div class="no-results">Enter a search term to get started.</div>';
      })
      .catch(error => {
        console.error('Error loading search index:', error);
        searchResults.innerHTML = '<div class="no-results">Error loading search index.</div>';
      });
  }

  /**
   * Perform search and display results
   */
  function performSearch(query, resultsContainer) {
    if (!query || query.trim() === '') {
      resultsContainer.innerHTML = '<div class="no-results">Enter a search term to get started.</div>';
      return;
    }

    if (!searchIndex) {
      resultsContainer.innerHTML = '<div class="search-loading">Loading search index...</div>';
      return;
    }

    try {
      // Perform search
      const results = searchIndex.search(query);

      if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="no-results">No results found for "' +
          escapeHtml(query) + '"</div>';
        return;
      }

      // Display results
      let html = '<p style="color: #666; margin-bottom: 1em;">Found ' +
        results.length + ' result' + (results.length > 1 ? 's' : '') +
        ' for "' + escapeHtml(query) + '"</p>';

      results.forEach(function(result) {
        const post = searchData[result.ref];
        html += formatSearchResult(post, query);
      });

      resultsContainer.innerHTML = html;

    } catch (error) {
      console.error('Search error:', error);
      resultsContainer.innerHTML = '<div class="no-results">Error performing search. Try a different query.</div>';
    }
  }

  /**
   * Format a search result
   */
  function formatSearchResult(post, query) {
    let html = '<div class="search-result">';

    // Title
    html += '<h3><a href="' + escapeHtml(post.url) + '">' +
      escapeHtml(post.title) + '</a></h3>';

    // Meta
    html += '<div class="search-result-meta">' +
      formatDate(post.date) + '</div>';

    // Excerpt with highlighting
    if (post.excerpt) {
      html += '<div class="search-result-excerpt">' +
        highlightText(post.excerpt, query) + '</div>';
    } else if (post.content) {
      const excerpt = post.content.substring(0, 200) + '...';
      html += '<div class="search-result-excerpt">' +
        highlightText(excerpt, query) + '</div>';
    }

    // Tags
    if (post.tags && post.tags.length > 0) {
      html += '<div class="search-result-tags">';
      post.tags.forEach(function(tag) {
        html += '<span class="tag">' + escapeHtml(tag) + '</span>';
      });
      html += '</div>';
    }

    html += '</div>';
    return html;
  }

  /**
   * Highlight search terms in text
   */
  function highlightText(text, query) {
    const escapedText = escapeHtml(text);
    const terms = query.toLowerCase().split(/\s+/);

    let result = escapedText;
    terms.forEach(function(term) {
      if (term.length > 2) {
        const regex = new RegExp('(' + escapeRegex(term) + ')', 'gi');
        result = result.replace(regex, '<mark>$1</mark>');
      }
    });

    return result;
  }

  /**
   * Format date
   */
  function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
  }

  /**
   * Escape HTML
   */
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Escape regex special characters
   */
  function escapeRegex(text) {
    return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

})();
