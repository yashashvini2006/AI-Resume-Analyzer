import streamlit as st
from pypdf import PdfReader
import google.generativeai as genai
import re
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from xml.sax.saxutils import escape


# =========================
# PAGE SETTINGS
# =========================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🤖",
    layout="centered"
)


# =========================
# GEMINI API
# =========================

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-3.6-flash")


# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>

.main-title {
    font-size: 44px;
    font-weight: 800;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    margin-bottom: 30px;
}

div.stButton > button {
    width: 100%;
    border-radius: 10px;
    font-size: 17px;
    font-weight: 600;
    padding: 10px;
}

div.stDownloadButton > button {
    width: 100%;
    border-radius: 10px;
    font-size: 17px;
    font-weight: 600;
    padding: 10px;
}

[data-testid="stMetric"] {
    border-radius: 12px;
    padding: 15px;
    border: 1px solid #ddd;
}

</style>
""", unsafe_allow_html=True)


# =========================
# TITLE
# =========================

st.markdown(
    '<div class="main-title">🤖 AI Resume Analyzer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Analyze your resume, improve your ATS score and get AI-powered feedback'
    '</div>',
    unsafe_allow_html=True
)


# =========================
# RESUME UPLOAD
# =========================

st.subheader("📄 Upload Your Resume")

uploaded_file = st.file_uploader(
    "Choose your resume PDF",
    type=["pdf"]
)


# =========================
# JOB DESCRIPTION
# =========================

st.subheader("💼 Job Description")

job_description = st.text_area(
    "Paste the job description here",
    height=180,
    placeholder="Paste the job description of the job you are applying for..."
)


# =========================
# ANALYZE
# =========================

if uploaded_file is not None:

    st.success("✅ Resume uploaded successfully!")

    if st.button("🔍 Analyze Resume"):

        # =========================
        # EXTRACT PDF TEXT
        # =========================

        reader = PdfReader(uploaded_file)

        resume_text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                resume_text += page_text + "\n"


        # =========================
        # CHECK PDF
        # =========================

        if not resume_text.strip():

            st.error(
                "❌ Could not extract text from this PDF."
            )

            st.stop()


        text = resume_text.lower()


        # =========================
        # SKILLS
        # =========================

        skills = [
            "python",
            "java",
            "c",
            "c++",
            "sql",
            "html",
            "css",
            "javascript",
            "react",
            "machine learning",
            "data science",
            "excel",
            "power bi",
            "tableau",
            "communication",
            "leadership"
        ]

        found_skills = []

        for skill in skills:

            if skill in text:
                found_skills.append(skill)


        # =========================
        # SKILLS DISPLAY
        # =========================

        st.subheader("🧑‍💻 Skills Detected")

        if found_skills:

            for skill in found_skills:

                st.success(
                    "✓ " + skill.title()
                )

        else:

            st.warning(
                "No matching skills found."
            )


        # =========================
        # RESUME SCORE
        # =========================

        score = min(
            len(found_skills) * 5,
            100
        )

        st.subheader("📊 Resume Score")

        st.progress(score / 100)

        st.metric(
            "Resume Score",
            f"{score}/100"
        )


        # =========================
        # RECOMMENDED SKILLS
        # =========================

        st.subheader(
            "💡 Recommended Skills"
        )

        recommended_skills = [
            "Python",
            "SQL",
            "Machine Learning",
            "Communication",
            "Data Analysis"
        ]

        missing_skills = []

        for skill in recommended_skills:

            if skill.lower() not in text:

                missing_skills.append(skill)


        if missing_skills:

            for skill in missing_skills:

                st.info(
                    "➕ " + skill
                )

        else:

            st.success(
                "🎉 Your resume contains all recommended skills!"
            )


        # =========================
        # AI ANALYSIS
        # ONE GEMINI CALL ONLY
        # =========================

        st.subheader(
            "🤖 AI Resume Feedback"
        )

        ats_text = ""
        ai_feedback = ""
        ats_score = 0


        if job_description.strip():

            combined_prompt = f"""
You are a professional resume and ATS analyzer.

Analyze the following resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return the answer EXACTLY using these sections:

RESUME SUMMARY:
Write a short professional summary.

STRENGTHS:
- strength 1
- strength 2
- strength 3

WEAKNESSES:
- weakness 1
- weakness 2
- weakness 3

MISSING SKILLS:
- skill 1
- skill 2
- skill 3

IMPROVEMENT SUGGESTIONS:
- suggestion 1
- suggestion 2
- suggestion 3

ATS SCORE: <number between 0 and 100>

MATCHING SKILLS:
- skill 1
- skill 2
- skill 3

ATS MISSING SKILLS:
- skill 1
- skill 2
- skill 3

MISSING KEYWORDS:
- keyword 1
- keyword 2
- keyword 3

ATS SUGGESTIONS:
- suggestion 1
- suggestion 2
- suggestion 3

Keep the language simple and useful for a student/fresher.
"""

        else:

            combined_prompt = f"""
You are a professional resume analyzer.

Analyze the following resume.

RESUME:
{resume_text}

Return the answer EXACTLY using these sections:

RESUME SUMMARY:
Write a short professional summary.

STRENGTHS:
- strength 1
- strength 2
- strength 3

WEAKNESSES:
- weakness 1
- weakness 2
- weakness 3

MISSING SKILLS:
- skill 1
- skill 2
- skill 3

IMPROVEMENT SUGGESTIONS:
- suggestion 1
- suggestion 2
- suggestion 3

Do not provide ATS analysis because no job description was supplied.

Keep the language simple and useful for a student/fresher.
"""


        # =========================
        # GEMINI REQUEST
        # =========================

        try:

            with st.spinner(
                "🤖 AI is analyzing your resume..."
            ):

                response = model.generate_content(
                    combined_prompt
                )

            result_text = response.text


            # =========================
            # DISPLAY AI FEEDBACK
            # =========================

            st.markdown(
                result_text
            )


            # =========================
            # SAVE AI FEEDBACK
            # =========================

            ai_feedback = result_text


            # =========================
            # ATS SCORE
            # =========================

            if job_description.strip():

                score_match = re.search(
                    r"ATS\s*SCORE\s*:\s*(\d+)",
                    result_text,
                    re.IGNORECASE
                )

                if score_match:

                    ats_score = int(
                        score_match.group(1)
                    )

                    ats_score = min(
                        max(ats_score, 0),
                        100
                    )


                    st.subheader(
                        "🎯 ATS Match Score"
                    )

                    st.metric(
                        "ATS Match Score",
                        f"{ats_score}/100"
                    )

                    st.progress(
                        ats_score / 100
                    )


                    st.success(
                        "✅ ATS analysis completed successfully!"
                    )

                else:

                    st.warning(
                        "⚠️ ATS score could not be detected."
                    )


        # =========================
        # API ERROR
        # =========================

        except Exception as e:

            error_text = str(e)

            if "429" in error_text or "ResourceExhausted" in error_text:

                st.error(
                    "⚠️ Gemini API quota exceeded."
                )

                st.info(
                    "Please wait for the quota to reset and try again."
                )

            else:

                st.error(
                    "❌ AI analysis failed."
                )

                st.write(
                    error_text
                )


        # =========================
        # PDF REPORT
        # =========================

        st.subheader(
            "📥 Download Your Report"
        )

        pdf_buffer = BytesIO()

        document = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        title_style.alignment = TA_CENTER

        heading_style = styles["Heading2"]
        body_style = styles["BodyText"]

        story = []


        # =========================
        # PDF TITLE
        # =========================

        story.append(
            Paragraph(
                "AI Resume Analysis Report",
                title_style
            )
        )

        story.append(
            Spacer(1, 20)
        )


        # =========================
        # RESUME SCORE
        # =========================

        story.append(
            Paragraph(
                f"<b>Resume Score:</b> {score}/100",
                body_style
            )
        )

        story.append(
            Spacer(1, 10)
        )


        # =========================
        # ATS SCORE
        # =========================

        if job_description.strip():

            story.append(
                Paragraph(
                    f"<b>ATS Match Score:</b> {ats_score}/100",
                    body_style
                )
            )

            story.append(
                Spacer(1, 15)
            )


        # =========================
        # SKILLS
        # =========================

        story.append(
            Paragraph(
                "Skills Detected",
                heading_style
            )
        )

        if found_skills:

            for skill in found_skills:

                story.append(
                    Paragraph(
                        "• " + escape(skill.title()),
                        body_style
                    )
                )

        else:

            story.append(
                Paragraph(
                    "No matching skills found.",
                    body_style
                )
            )


        story.append(
            Spacer(1, 15)
        )


        # =========================
        # MISSING SKILLS
        # =========================

        story.append(
            Paragraph(
                "Recommended / Missing Skills",
                heading_style
            )
        )

        if missing_skills:

            for skill in missing_skills:

                story.append(
                    Paragraph(
                        "• " + escape(skill),
                        body_style
                    )
                )

        else:

            story.append(
                Paragraph(
                    "No recommended skills are missing.",
                    body_style
                )
            )


        story.append(
            Spacer(1, 15)
        )


        # =========================
        # AI FEEDBACK
        # =========================

        story.append(
            Paragraph(
                "AI Resume Feedback",
                heading_style
            )
        )


        for line in ai_feedback.split("\n"):

            if line.strip():

                story.append(
                    Paragraph(
                        escape(line),
                        body_style
                    )
                )

                story.append(
                    Spacer(1, 5)
                )


        # =========================
        # BUILD PDF
        # =========================

        document.build(
            story
        )

        pdf_buffer.seek(0)

        pdf_data = pdf_buffer.getvalue()


        # =========================
        # DOWNLOAD BUTTON
        # =========================

        st.download_button(
            label="📄 Download Resume Analysis Report",
            data=pdf_data,
            file_name="AI_Resume_Analysis_Report.pdf",
            mime="application/pdf"
        )

        st.success(
            "✅ Your resume report is ready!"
        )