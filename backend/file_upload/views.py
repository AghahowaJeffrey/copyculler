import os
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from .serializers import FileUploadSerializer
from .services import handle_final_chunked_upload, clear_cache_for_session


class FileUploadView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key

        print('session_key', session_key)

        # Check if this is a new session
        if 'new_session' in request.POST:
            clear_cache_for_session(session_key)  # Clear previous session data

        # Check upload limit
        upload_count = cache.get(f"upload_count_{session_key}", 0)
        files = request.FILES.getlist('files')
        print("FILES RECEIVED:", files)

        if upload_count + len(files) > 5 or upload_count >= 5:
            return Response({
                'error': 'You can only upload up to 5 files per session.',
            }, status=status.HTTP_400_BAD_REQUEST)
        

        for file in files:
            if upload_count >= 5:
                break  # Stop if the upload limit is reached

            # Validate file upload
            serializer = FileUploadSerializer(data={'file': file})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Handle chunked upload (if applicable)
            if 'chunk_index' in request.data and 'total_chunks' in request.data:
                # Chunked upload logic
                chunk_index = int(request.data.get('chunk_index', 0))
                total_chunks = int(request.data.get('total_chunks', 1))
                print('chunk_index', chunk_index)
                print('total_chunks', total_chunks)

                # Save the chunk to a temporary location
                chunk_dir = f"uploads/{session_key}/{upload_count}"  # Separate directory per file
                os.makedirs(chunk_dir, exist_ok=True)
                chunk_path = f"{chunk_dir}/{chunk_index}"
                with open(chunk_path, 'wb') as chunk_file:
                    for chunk in file.chunks():
                        chunk_file.write(chunk)

                # Check if all chunks have been uploaded
                if chunk_index == total_chunks - 1:
                    # Reassemble the file
                    file_path = f"{chunk_dir}/complete_file"
                    with open(file_path, 'wb') as final_file:
                        for i in range(total_chunks):
                            chunk_path = f"{chunk_dir}/{i}"
                            with open(chunk_path, 'rb') as chunk_file:
                                final_file.write(chunk_file.read())
                            os.remove(chunk_path)  # Delete the chunk after reassembly

                    cache_key = f"file_{session_key}_{upload_count}"

                    handle_final_chunked_upload(file_path, cache_key)
                    
                    os.rmdir(chunk_dir)
            else:
                # Non-chunked upload (single file)
                cache_key = f"file_{session_key}_{upload_count}"
                cache.set(cache_key, file.read(), timeout=3600)
                
            upload_count += 1
            cache.set(f"upload_count_{session_key}", upload_count, timeout=3600)
            
        return Response({
            'message': 'File uploaded successfully.',
            'upload_count': upload_count,
        }, status=status.HTTP_200_OK)
    