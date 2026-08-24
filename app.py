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

.info-box {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin: 15px 0;
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
# UPLOAD RESUME
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
# ANALYZE BUTTON
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
                resume_text += page_text


        if not resume_text.strip():

            st.error(
                "❌ Could not extract text from this PDF."
            )

        else:

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

            st.progress(
                score / 100
            )

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
            # GEMINI AI FEEDBACK
            # =========================

            st.subheader(
                "🤖 AI Resume Feedback"
            )

            model = genai.GenerativeModel(
                "gemini-3.6-flash"
            )

            prompt = f"""
Analyze this resume and provide professional feedback.

Give:

1. Resume Summary
2. Strengths
3. Weaknesses
4. Missing Skills
5. Improvement Suggestions

Keep the feedback simple and useful for a student/fresher.

Resume:

{resume_text}
"""

            ai_feedback = ""

            try:

                response = model.generate_content(
                    prompt
                )

                ai_feedback = response.text

                st.write(
                    ai_feedback
                )

            except Exception as e:

                ai_feedback = (
                    "AI analysis could not be generated."
                )

                st.error(
                    "AI analysis failed"
                )

                st.write(e)


            # =========================
            # ATS ANALYSIS
            # =========================

            ats_text = ""
            ats_score = 0

            if job_description.strip():

                st.subheader(
                    "🎯 ATS Match Analysis"
                )

                ats_prompt = f"""
Compare this resume with the job description.

Resume:

{resume_text}

Job Description:

{job_description}

Return your answer EXACTLY in this format:

ATS SCORE: <number between 0 and 100>

MATCHING SKILLS:
- skill 1
- skill 2
- skill 3

MISSING SKILLS:
- skill 1
- skill 2
- skill 3

MISSING KEYWORDS:
- keyword 1
- keyword 2
- keyword 3

SUGGESTIONS:
- suggestion 1
- suggestion 2
- suggestion 3
"""

                try:

                    ats_response = model.generate_content(
                        ats_prompt
                    )

                    ats_text = ats_response.text


                    # =========================
                    # ATS SCORE
                    # =========================

                    score_match = re.search(
                        r"ATS SCORE\s*:\s*(\d+)",
                        ats_text,
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

                        st.metric(
                            "🎯 ATS Match Score",
                            f"{ats_score}/100"
                        )

                        st.progress(
                            ats_score / 100
                        )

                    else:

                        st.warning(
                            "Could not detect ATS score."
                        )


                    # =========================
                    # ATS DETAILS
                    # =========================

                    st.markdown(
                        "### 📋 Detailed ATS Analysis"
                    )

                    st.write(
                        ats_text
                    )


                except Exception as e:

                    st.error(
                        "ATS analysis failed"
                    )

                    st.write(e)

            else:

                st.info(
                    "💡 Paste a job description to get ATS analysis."
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


            # TITLE

            story.append(
                Paragraph(
                    "AI Resume Analysis Report",
                    title_style
                )
            )

            story.append(
                Spacer(1, 20)
            )


            # RESUME SCORE

            story.append(
                Paragraph(
                    f"<b>Resume Score:</b> {score}/100",
                    body_style
                )
            )

            story.append(
                Spacer(1, 10)
            )


            # ATS SCORE

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


            # SKILLS

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


            # MISSING SKILLS

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


            # AI FEEDBACK

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


            # ATS DETAILS

            if job_description.strip() and ats_text:

                story.append(
                    Spacer(1, 10)
                )

                story.append(
                    Paragraph(
                        "ATS Analysis",
                        heading_style
                    )
                )

                for line in ats_text.split("\n"):

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


            # BUILD PDF

            document.build(
                story
            )

            pdf_buffer.seek(0)

            pdf_data = pdf_buffer.getvalue()


            # =========================
            # DOWNLOAD
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