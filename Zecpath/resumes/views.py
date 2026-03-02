from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Resume
from .utils import ResumeTextExtractor,ResumeParser
from .parser import parse_resume

class ResumeUploadAPI(APIView):

    permission_classes = [IsAuthenticated]


    def post(self, request):

        file = request.FILES.get("file")

        resume = Resume.objects.create(
            user=request.user,
            file=file
        )

        text = ResumeTextExtractor.extract(resume.file.path)

        resume.extracted_text = text
        resume.save()

        return Response({

            "message": "Resume uploaded successfully",

            "resume_id": resume.id,

            "extracted_text": text

        })
    
class ResumeUploadParseAPI(APIView):

    permission_classes = [IsAuthenticated]
    def post(self, request):

        file = request.FILES.get("file")

        if not file:
            return Response({"error": "No file uploaded"})


        resume = Resume.objects.create(
            user=request.user,
            file=file
        )
#  Extract text
        text = ResumeTextExtractor.extract_text(resume.file.path)
#  Parse data
        email = ResumeParser.extract_email(text)

        phone = ResumeParser.extract_phone(text)

        skills = ResumeParser.extract_skills(text)
#  Save parsed data
        resume.extracted_text = text
        resume.email = email
        resume.phone = phone
        resume.skills = skills
        resume.save()
#  Return response
        return Response({"success": True,"resume_id": resume.id,"email": email,"phone": phone,"skills": skills,"text": text
        })
    
class ResumeUploadView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        file = request.FILES.get("file")

        resume = Resume.objects.create(
            candidate=request.user,
            file=file
        )

        text = file.read().decode("utf-8", errors="ignore")

        parsed = parse_resume(text)

        resume.parsed_data = parsed
        resume.save()

        return Response({
            "success": True,
            "data": parsed
        })