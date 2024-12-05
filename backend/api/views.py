from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import JsonResponse
from openai import OpenAI
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserRegistrationSerializer

TOKEN = "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"
endpoint = "https://models.inference.ai.azure.com"

client = OpenAI(
    base_url=endpoint,
    api_key=TOKEN,
)
# Prepare the messages for the OpenAI API request
cryptography_dataset = [
    {"role": "system", "content": "You are a Cybersecurity expert assistant."},
    {"role": "user",
     "content": "Generate a dataset of scenario-based multiple-choice questions on the topic of Cryptography (Domain) in Cybersecurity. The question should frame a real-world cryptography task, incident, or theoretical challenge. Make the question feel like a practical exercise, decision-making scenario, or troubleshooting task. Include only one correct answer and two or three plausible distractors. The Correct Answer includes just the Letter. Generate exactly 9 unique questions, equally divided into 3 easy, 3 medium, and 3 hard. Please format the output as plain text, separating each field with a semicolon, and do not include any extra characters.\n"
                "Example: Question;Option A;Option B;Option C;Option D;Correct Answer;Explanation; Difficulty; Domain"
                "Your company’s network uses symmetric encryption to secure data during transmission. Which of the following cryptographic questions must be asked first to ensure key management is effective?;Are keys being changed regularly?;Is the encryption algorithm current?;Are the keys long enough?;Is the encryption method approved by industry standards?;A;Effective key management involves regular changing of keys to prevent unauthorized access.;Easy;Cryptography"

     }
]

# Prepare the messages for the OpenAI API request
network_security_dataset = [
    {"role": "system", "content": "You are a Network security expert assistant."},
    {"role": "user",
     "content": "Generate a dataset of scenario-based multiple-choice questions on the topic of network security (Domain) in Cybersecurity. The question should frame a real-world network security task, incident, or theoretical challenge. Make the question feel like a practical exercise, decision-making scenario, or troubleshooting task. Include only one correct answer and two or three plausible distractors. The Correct Answer includes just the Letter. Generate exactly 9 unique questions, equally divided into 3 easy, 3 medium, and 3 hard. Please format the output as plain text, separating each field with a semicolon, and do not include any extra characters."
                "Example: Question;Option A;Option B;Option C;Option D;Correct Answer;Explanation; Difficulty; Domain"
                "You're reviewing network logs and see many requests for non-existent files from the same IP, often resulting in error code 404. What is the MOST likely explanation?;SQL injection attempt; Cross-Site Scripting attack;Directory traversal attack; Port scanning activity;C; Repeated attempts to access invalid files suggest directory traversal, where an attacker probes for hidden directories/files. 404 errors are typical responses to non-existent resources. SQLi targets databases, XSS injects malicious code, and port scanning checks open ports.;Medium;Network Security."
     }
]

operating_systems_security_dataset = [
    {"role": "system", "content": "You are an Operating Systems Security expert assistant."},
    {"role": "user",
     "content": "Generate a dataset of scenario-based multiple-choice questions on the topic of operating systems security (Domain) in Cybersecurity. The question should frame a real-world operating systems security task, incident, or theoretical challenge. Make the question feel like a practical exercise, decision-making scenario, or troubleshooting task. Include only one correct answer and two or three plausible distractors. The Correct Answer includes just the Letter. Generate exactly 9 unique questions, equally divided into 3 easy, 3 medium, and 3 hard. Please format the output as plain text, separating each field with a semicolon, and do not include any extra characters. Includes multiple operating systems (Windows, Linux, macOS).\n"
                "Example: Question;Option A;Option B;Option C;Option D;Correct Answer;Explanation; Difficulty; Domain"
     }
]

digital_forensic_dataset = [
    {"role": "system", "content": "You are a Digital Forensics expert assistant."},
    {"role": "user",
     "content": "Generate a dataset of scenario-based multiple-choice questions on the topic of Digital Forensics (Domain) in Cybersecurity. The question should frame a real-world Digital Forensics task, incident, or theoretical challenge. Make the question feel like a practical exercise, decision-making scenario, or troubleshooting task. Include only one correct answer and two or three plausible distractors. The Correct Answer includes just the Letter. Generate exactly 9 unique questions, equally divided into 3 easy, 3 medium, and 3 hard. Please format the output as plain text, separating each field with a semicolon, and do not include any extra characters.\n"
                "Example: Question;Option A;Option B;Option C;Option D;Correct Answer;Explanation; Difficulty; Domain\n"
                "While investigating a potential data breach, you discover that the attacker used a steganography technique to hide data within image files. What is the first step you should take to uncover this hidden data?;Use a file integrity checker;Perform a hash analysis;Utilize a steganography detection tool;Inspect the file metadata manually;C;Using a steganography detection tool is the most direct method to uncover hidden data in images.;Easy;Digital Forensics"
     }
]

application_security_dataset = [
    {"role": "system", "content": "You are an Application Security expert assistant."},
    {"role": "user",
     "content": "Generate a dataset of scenario-based multiple-choice questions on the topic of applications security (Domain), either Web or Mobile in Cybersecurity. The question should frame a real-world application security task, incident, or theoretical challenge. Make the question feel like a practical exercise, decision-making scenario, or troubleshooting task. Include only one correct answer and two or three plausible distractors. The Correct Answer includes just the Letter. Generate exactly 9 unique questions, equally divided into 3 easy, 3 medium, and 3 hard. Please format the output as plain text, separating each field with a semicolon, and do not include any extra characters.\n"
                "Example: Question;Option A;Option B;Option C;Option D;Correct Answer;Explanation; Difficulty; Domain"
     }
]

iam_management_dataset = [
    {"role": "system", "content": "You are an Identity and Access Management expert assistant."},
    {"role": "user",
     "content": "Generate a dataset of scenario-based multiple-choice questions on the topic of identity and access management (Domain) in Cybersecurity. The question should frame a real-world identity and access management (Autenticação multifatorial, RBAC, Protocol OAuth, SAML e OpenID Connect, privilages managment) task, incident, or theoretical challenge. Make the question feel like a practical exercise, decision-making scenario, or troubleshooting task. Include only one correct answer and two or three plausible distractors. The Correct Answer includes just the Letter. Generate exactly 9 unique questions, equally divided into 3 easy, 3 medium, and 3 hard. Please format the output as plain text, separating each field with a semicolon, and do not include any extra characters. \n"
                "Example: Question;Option A;Option B;Option C;Option D;Correct Answer;Explanation; Difficulty; Domain"
                "Which component ensures that the user's identity is passed correctly in an OpenID Connect flow to the relying party application?; Resource Owner;Authorization Server;Identity Token;Client Secret;C;An identity token is issued by the authorization server and contains claims about the authentication state, ensuring the relying party application (client) correctly identifies the user.;Medium;IAM"
     }
]

cloud_security_dataset = [
    {"role": "system", "content": "You are a Cloud Security expert assistant."},
    {"role": "user",
     "content": "Generate a dataset of scenario-based multiple-choice questions on the topic of cloud security (Domain) in Cybersecurity. The question should frame a real-world cloud security task, incident, or theoretical challenge. Make the question feel like a practical exercise, decision-making scenario, or troubleshooting task. Include only one correct answer and two or three plausible distractors. The Correct Answer includes just the Letter. Generate exactly 9 unique questions, equally divided into 3 easy, 3 medium, and 3 hard. Please format the output as plain text, separating each field with a semicolon, and do not include any extra characters."
                "Example: Question;Option A;Option B;Option C;Option D;Correct Answer;Explanation; Difficulty; Domain"
                "Which cloud deployment model provides users with virtualized computing resources, such as servers and storage, but requires them to manage the operating system and applications?;Software as a Service (SaaS);Platform as a Service (PaaS);Infrastructure as a Service (IaaS);Cloud Access Security Broker (CASB);C;Infrastructure as a Service (IaaS) provides virtualized computing resources over the internet, giving users control over the operating system, middleware, and applications while the provider manages the physical hardware.;Medium;Cloud Security"
     }
]


# Create your views here.
def main(request):
    return Response("<h1>Hello, world...</h1>")


def ask_gpt(request):
    try:
        # Send request to the OpenAI API
        response = client.chat.completions.create(
            messages=cloud_security_dataset,
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model="gpt-4o"
        )

        content = response.choices[0].message.content.strip()

        return HttpResponse(f"<pre>{content}</pre>", content_type="text/html")

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow registration without authentication
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        # Save the user in db
        user = serializer.save()

        return JsonResponse(
            {
                "message": "User registered successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            },
            status=status.HTTP_201_CREATED,
        )
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)

        # Blacklist the refresh token to invalidate it
        token.blacklist()

        return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)

    except Exception as e:
        # If there is an error (e.g., the refresh token is invalid), return an error message
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
