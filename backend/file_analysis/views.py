from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from ..models import AnalysisSession, UploadedFile
from ..services.comparison_service import FileComparator

class FileUploadView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        session = AnalysisSession.objects.create()
        files = request.FILES.getlist('files')
        
        # Save files and extract text
        texts = []
        for file in files:
            uploaded_file = UploadedFile.objects.create(session=session, file=file)
            text = FileComparator().extract_text(uploaded_file.file.path)
            uploaded_file.processed_text = text
            uploaded_file.save()
            texts.append(text)
        
        # Perform AI-powered comparison
        comparator = FileComparator()
        common_content = comparator.find_common_sections(texts)
        unique_contents = comparator.find_unique_sections(texts)
        
        # Generate summaries
        common_summary = comparator.summarize_text(common_content)
        unique_summaries = [comparator.summarize_text(unique) for unique in unique_contents]
        
        # Prepare response
        response_data = {
            'session_id': str(session.session_id),
            'common_content': common_content,
            'common_summary': common_summary,
            'unique_contents': unique_contents,
            'unique_summaries': unique_summaries,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)