from django.core.cache import cache

def save_file_to_cache(file_data, session_key, file_index):
    """Save file data to cache."""
    cache_key = f"file_{session_key}_{file_index}"
    cache.set(cache_key, file_data, timeout=3600)  # Cache for 1 hour

def get_file_from_cache(session_key, file_index):
    """Retrieve file data from cache."""
    cache_key = f"file_{session_key}_{file_index}"
    return cache.get(cache_key)

def clear_cache_for_session(session_key):
    """Clear cached files for a session."""
    for i in range(5):  # Max 5 files
        cache_key = f"file_{session_key}_{i}"
        cache.delete(cache_key)
    cache.delete(f"upload_count_{session_key}")

def process_files(session_key):
    """Process files from cache."""
    file_data_list = []
    for i in range(5):  # Max 5 files
        file_data = get_file_from_cache(session_key, i)
        if file_data:
            file_data_list.append(file_data)

    # Process files (e.g., extract text, vectorize)
    results = []
    for file_data in file_data_list:
        text = extract_text_from_data(file_data)  # Implement this function
        embeddings = vectorize_text(text)  # Implement this function
        results.append({
            'text': text,
            'embeddings': embeddings,
        })

    return results

def handle_final_chunked_upload(file_path, cache_key):
    with open(file_path, 'rb') as final_file:
        cache.set(cache_key, final_file.read(), timeout=3600)
        print('cache_key', cache_key)