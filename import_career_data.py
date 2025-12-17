"""
Import career data into supermemory for resume/cover letter generation.

This script populates supermemory with structured career information including:
- Job history with context
- Quantifiable achievements
- Skills with evidence
- Writing style patterns
- Personal values and motivations
"""

import os
import sys

# Add the parent directory to the path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Career data structure based on Watson's resumes and cover letters
CAREER_DATA = {
    "contact_info": {
        "name": "M. Watson Mulkey",
        "email": "watsonmulkey@gmail.com",
        "phone": "434-808-2493",
        "linkedin": "linkedin.com/in/watsonmulkey",
        "location": "Denver, Colorado"
    },

    "personal_values": [
        {
            "content": "Personal mission alignment: Most rewarding PM experiences came from education space (Discovery Education) and Certified B corporations (Bookshop.org). Emotional and value alignment produces best work and fulfillment. Started in tech at a coding school supporting career changers.",
            "category": "values"
        },
        {
            "content": "Personal story - therapy impact: 'Finding a therapist and getting mental health treatment changed my life. I would love to use my 8 years of Product Management experience to help more people untangle their Christmas lights, and change their lives for the better with therapy.'",
            "category": "personal_story"
        },
        {
            "content": "Career motivation: Seeks meaningful work that creates economic mobility, supports education, and works with mission-driven organizations (B-corps, education sector).",
            "category": "values"
        }
    ],

    "job_history": [
        {
            "title": "Senior Product Manager - ID/Onboarding/Platform",
            "company": "Registria",
            "dates": "01/2024 - 03/2025",
            "location": "Denver, Colorado",
            "company_context": "Post-purchase consumer care, management, and insights for major consumer brands (Sony, Whirlpool, Fujifilm, etc)",
            "responsibilities": [
                "Delivered and maintain comprehensive reporting suite for flagship product, delivering actionable insights to internal stakeholders and external clients",
                "Develop and maintain multi-vertical dependency roadmap",
                "Create consensus between sales, customer success, engineering, and clients for features that are both valuable and scalable",
                "Building contextual user experience engine to provide unique customer insights for brands",
                "Leading updates and migrations of legacy services and products",
                "Collaborate cross-functionally to optimize engineering output through improved workflows and strategic alignment"
            ]
        },
        {
            "title": "Product Manager - Teacher Tools",
            "company": "Discovery Education",
            "dates": "11/2021 - 12/2023",
            "location": "Charlotte, North Carolina",
            "company_context": "Industry leading edtech platform with 50M global user base, 1M+ MAU",
            "responsibilities": [
                "Lead a team of 4-7 (design, dev, QA) and manage several large projects of 20+ people across 5 different teams",
                "Analyze and Report on data trends, A/B test results, and usage metrics to executives and stakeholders on a monthly basis",
                "Partnering with data team for A/B testing and developing data/reporting pipelines for key user flows",
                "Create and deliver monthly presentations on data trends, A/B progress results, usage metrics for C Suite and Executives",
                "Working with Product Marketing to develop strategies for increased new feature visibility for sales and other client facing teams"
            ]
        },
        {
            "title": "Product Consultant",
            "company": "Bookshop.org",
            "dates": "12/2020 - Present",
            "location": "New York, New York",
            "company_context": "Independent online bookseller with over $50M in annual revenue. Led product for all e-commerce, including search and discovery, personalization and checkout. Brought in to help manage growing pains after tremendous growth.",
            "responsibilities": [
                "Helping refine and validate short and long term product strategy for global business units",
                "Create product processes and agile ceremonies that allow for globally distributed development team to work asynchronously",
                "Training an internally selected employee to be a product manager",
                "Establishing cross-functional product relations with new and existing business units",
                "Explaining agile, developmental, and PM concepts to less technical users",
                "Documenting all work and helping create internal company-wide data and process resource"
            ]
        },
        {
            "title": "Product Manager",
            "company": "Simplifya",
            "dates": "01/2019 - 03/2021",
            "location": "Denver, Colorado",
            "company_context": "Cannabis compliance software serving individual businesses, insurance agencies, banks, and multinational companies",
            "responsibilities": [
                "Conducted user interviews and acceptance testing across various segments and personas to stay on pace with constantly evolving client needs",
                "Investigated market trends and conducted competitive analysis to create multi-product roadmap",
                "Created sales enablement content through feature demos, sales scripts, release notes, blog posts, feature announcements"
            ]
        },
        {
            "title": "Product Manager",
            "company": "Helix Education",
            "dates": "11/2017 - 12/2018",
            "location": "Denver, Colorado",
            "company_context": "Outsourced pipeline management for higher education enrollment growth through data-driven services and technologies",
            "responsibilities": [
                "Develop and maintain multi-year product roadmap with emphasis on functional needs",
                "Interviewing users and stakeholders for internal/group software applications",
                "Developing new online application portal to streamline application experience and greatly improve data uniformity",
                "Assist sales and operations with prospecting activities (discovery, assessments, RFPs, scoping, etc.)",
                "Conducting product demos for existing and prospective clients",
                "Lead contracting and work negotiations with 3rd party vendors and contractors",
                "Participate in development team, QA, acceptance testing, and product reviews"
            ]
        },
        {
            "title": "Product Support Lead",
            "company": "The Iron Yard",
            "dates": "04/2017 - 09/2017",
            "location": "Denver, Colorado",
            "company_context": "12-week intensive coding school. Promoted to be the first product person on Newline, an internal CMS and external learning tool.",
            "responsibilities": [
                "Manage feedback and consolidate user problems for Newline",
                "Total ownership of Customer Support functions. Created issue tracking system that reduced open ticket time by 40%",
                "Manage technical challenges for hundreds of students and staff",
                "Creation and distribution of support documents in anticipation of and in response to customer and staff challenges"
            ]
        }
    ],

    "achievements": [
        {
            "achievement": "Improved user engagement on flagship product by 32% YoY",
            "company": "Discovery Education",
            "context": "Was tasked with increasing new user engagement (teachers setting up classroom and assigning content more than once). Talked with teachers and educators to understand how schedules, resources, curriculums, and support systems informed their needs. Overhauled teacher side of app to remove common friction points.",
            "metrics": "32% Year-over-Year engagement increase",
            "scope": "1M+ MAU, 50M global user base",
            "methods": "User interviews, stakeholder research, UX overhaul, friction point removal"
        },
        {
            "achievement": "Identified user flow responsible for losing 33% of traffic and recovered 10%",
            "company": "Discovery Education",
            "context": "Partnered with data team to develop way to test hypothesis and found hundreds of thousands of users churning during specific flow. Refactored flow to recapture 10% within first month.",
            "metrics": "33% traffic loss identified, 10% recovered in first month",
            "scope": "Hundreds of thousands of users",
            "methods": "Data analysis, hypothesis testing, user flow optimization"
        },
        {
            "achievement": "15% increase in delivery rate YoY",
            "company": "Discovery Education",
            "context": "Lead team of 4-7 (design, dev, QA) and managed several large projects of 20+ people across 5 different teams.",
            "metrics": "15% Year-over-Year delivery rate increase",
            "scope": "Cross-functional team of 20+ people across 5 teams",
            "methods": "Cross-functional team leadership, project management"
        },
        {
            "achievement": "Refactored flagship auditing product - 50% reduction in time-to-complete, 40% increase in usage YoY",
            "company": "Simplifya",
            "context": "Refactor of app's main feature (self-audit tool) enhancing efficiency and accessibility for diverse range of users.",
            "metrics": "50% reduction in completion time within a month, 40% usage increase YoY",
            "scope": "Flagship product serving individual businesses to multinational companies",
            "methods": "User interviews, acceptance testing, product refactoring"
        },
        {
            "achievement": "Built 0-1 product for new industry needs",
            "company": "Simplifya",
            "context": "Worked directly with large and small businesses to understand how needs were changing in constantly shifting regulatory environment where requirements were different state-to-state. Built new feature that met both multinational brands and single state operators' current needs.",
            "metrics": "Launched new feature from scratch",
            "scope": "Multinational brands and single-state operators",
            "methods": "Direct client collaboration, regulatory analysis, scalable feature design"
        },
        {
            "achievement": "Created issue tracking system reducing open ticket time by 40%",
            "company": "The Iron Yard",
            "context": "Total ownership of Customer Support functions for hundreds of students and staff.",
            "metrics": "40% reduction in open ticket time",
            "scope": "Hundreds of students and staff",
            "methods": "Process creation, issue tracking system design"
        }
    ],

    "skills": [
        {
            "skill": "Cross-functional Team Leadership",
            "evidence": [
                "Led team of 4-7 (design, dev, QA) at Discovery Education resulting in 15% increase in delivery rate YoY",
                "Managed projects of 20+ people across 5 different teams",
                "Create consensus between sales, customer success, engineering, and clients at Registria"
            ],
            "context": "Multiple roles across different companies and team sizes"
        },
        {
            "skill": "Data Analysis & A/B Testing",
            "evidence": [
                "Partnered with data team to identify user flow losing 33% of traffic",
                "Monthly presentations on data trends, A/B test results, usage metrics to C-Suite at Discovery",
                "Developed data/reporting pipelines for key user flows"
            ],
            "tools": ["Looker", "Fullstory", "Google Analytics"]
        },
        {
            "skill": "User Research & Voice of Customer",
            "evidence": [
                "Talked with teachers and educators at Discovery to understand schedules, resources, curriculums, support systems",
                "Talked to local bookshops and booksellers in US, UK, EU for Bookshop.org",
                "Conducted user interviews and acceptance testing across various segments at Simplifya",
                "Created user experience that demonstrated and respected independent bookstores' businesses in their countries"
            ],
            "context": "Experience with diverse user types: teachers, booksellers internationally, cannabis compliance users, students"
        },
        {
            "skill": "Product Strategy & Roadmapping",
            "evidence": [
                "Develop and maintain multi-vertical dependency roadmap at Registria",
                "Created multi-product roadmap at Simplifya through market trend investigation and competitive analysis",
                "Multi-year product roadmap with emphasis on functional needs at Helix Education"
            ]
        },
        {
            "skill": "Working with Less Technical Users",
            "evidence": [
                "Explaining agile, developmental, and PM concepts to less technical users at Bookshop.org",
                "Training internally selected employee to be product manager",
                "Working with teachers (Discovery), booksellers (Bookshop), compliance users (Simplifya)"
            ],
            "context": "Expertise in building scalable solutions for users constrained by resources, knowledge, compliance"
        },
        {
            "skill": "Stakeholder Management & Reporting",
            "evidence": [
                "Monthly presentations to C-Suite and Executives at Discovery",
                "Delivering actionable insights to internal stakeholders and external clients at Registria",
                "Assist sales and operations with prospecting activities, conducting product demos at Helix"
            ]
        },
        {
            "skill": "Process Creation & Agile Implementation",
            "evidence": [
                "Created product processes and agile ceremonies for globally distributed team at Bookshop.org",
                "Created issue tracking system reducing open ticket time by 40% at Iron Yard",
                "Documented all work helping create internal company-wide data and process resource"
            ]
        },
        {
            "skill": "SQL & Database Experience",
            "evidence": [
                "Hands-on experience writing SQL queries for data analysis",
                "Understanding of database structures and data modeling",
                "Technical background in working with data stacks"
            ],
            "tools": ["SQL", "Databases"]
        },
        {
            "skill": "Distributed/Async Team Collaboration",
            "evidence": [
                "Extensive experience working in fully remote/async teams",
                "Written-first communication approach for global collaboration",
                "Created product processes and agile ceremonies for globally distributed team at Bookshop.org"
            ],
            "context": "Global team collaboration across time zones"
        },
        {
            "skill": "Product Documentation & Requirements",
            "evidence": [
                "Writes detailed PRDs (Product Requirements Documents) with user stories and acceptance criteria",
                "Creates design briefs and UX/UI documentation for designers",
                "Frames user needs in actionable ways for engineering teams",
                "Documents features and epics for agile development"
            ],
            "types": ["PRDs", "User Stories", "Epics", "Design Briefs"]
        },
        {
            "skill": "API & Platform Thinking",
            "evidence": [
                "Significant experience with platform products and API design",
                "Built AI-powered applications with Claude API integration",
                "Designed RAG (Retrieval-Augmented Generation) architectures",
                "Experience with extensibility features and integrations"
            ],
            "context": "Platform architecture and developer tools"
        },
        {
            "skill": "AI & Modern Development Tools",
            "evidence": [
                "Built production AI applications using Claude API with RAG architecture",
                "Designed anti-hallucination patterns for factual accuracy in AI-generated content",
                "Integrated MCP (Model Context Protocol) servers for semantic data retrieval",
                "Experienced with prompt engineering and AI optimization for business use cases",
                "Developed full-stack applications using AI-assisted development workflows"
            ],
            "tools": ["Claude API", "Python", "Vue 3", "FastAPI", "MCP"],
            "context": "AI-assisted product development and AI integration"
        }
    ],

    "education": {
        "degree": "Bachelor of Arts - English",
        "school": "Hampden-Sydney College",
        "location": "Hampden-Sydney, Virginia",
        "dates": "08/2004 - 04/2008"
    },

    "certifications": [
        "Pragmatic Marketing - Focus: Find strategic business opportunities in market problems, build effective product roadmaps, and sell your vision with confidence",
        "Pragmatic Marketing - Foundations: Learn how to decode market needs and build irresistible products that people want to buy",
        "Pragmatic Marketing - Build: Master the art of aligning product development with market needs"
    ],

    "writing_style": {
        "cover_letter_structure": [
            "Opens with personal connection when mission-aligned",
            "Uses bullet-point structure to map job requirements to specific experience",
            "Quantifies achievements prominently",
            "Shows understanding of company context and challenges",
            "Ends with enthusiasm and forward-looking statement"
        ],
        "tone_patterns": [
            "Warm and enthusiastic ('really excited', 'would love')",
            "Professional but personal",
            "Mission-driven language when applicable",
            "Collaborative framing ('This is how you get from good to great')"
        ],
        "common_phrases": [
            "I'd love an opportunity to talk more about...",
            "Here's why I think I'd be a great fit...",
            "Thanks so much for the time and consideration",
            "look forward to speaking soon",
            "I'm really excited to submit my application"
        ],
        "opening_styles": [
            "Personal story connecting to mission (Headway: therapy changed life)",
            "Direct statement of enthusiasm (Guild: 'really excited to submit')",
            "Professional greeting with immediate value proposition"
        ],
        "requirement_mapping_style": "Takes job requirement in quotes, then provides specific example with company name, context, quantified outcome, and underlined metrics"
    },

    "cover_letter_examples": [
        {
            "company": "Headway",
            "opening": "Finding a therapist and getting mental health treatment changed my life. I would love to use my 8 years of Product Management experience to help more people 'untangle their Christmas lights', and change their lives for the better with therapy.",
            "structure_notes": "Maps each job requirement to specific experience with company context and metrics",
            "closing": "I'd love an opportunity to talk more about why I think I'd be a great fit, and look forward to an opportunity to do so."
        },
        {
            "company": "Guild",
            "opening": "My name is Watson, and I'm really excited to submit my application for the Senior Product Manager Academic position!",
            "themes": ["Mission and values alignment", "Meaningful Domain Expertise"],
            "closing": "I'm excited to talk more about why I'd be a great fit for Guild and this role, and would love an opportunity to do so. Thanks so much for the time and consideration, and I look forward to speaking soon!"
        }
    ]
}


def format_for_supermemory(data):
    """
    Convert career data into supermemory-ready entries.
    Each entry should be a self-contained piece of information.
    """
    entries = []

    # Contact information
    contact = data["contact_info"]
    entries.append({
        "content": f"""CONTACT INFORMATION:
Name: {contact['name']}
Email: {contact['email']}
Phone: {contact['phone']}
LinkedIn: {contact['linkedin']}
Location: {contact['location']}""",
        "tags": ["contact_info", "personal"]
    })

    # Personal values and stories
    for item in data["personal_values"]:
        entries.append({
            "content": f"[{item['category'].upper()}] {item['content']}",
            "tags": ["personal", item["category"], "values"]
        })

    # Job history - one entry per job
    for job in data["job_history"]:
        job_entry = f"""JOB: {job['title']} at {job['company']} ({job['dates']})
Location: {job['location']}
Company Context: {job['company_context']}

Key Responsibilities:
{chr(10).join('- ' + r for r in job['responsibilities'])}"""

        entries.append({
            "content": job_entry,
            "tags": ["job_history", job["company"].replace(" ", "_").lower(), "experience"]
        })

    # Achievements - granular, searchable
    for achievement in data["achievements"]:
        achievement_entry = f"""ACHIEVEMENT: {achievement['achievement']}

Company: {achievement['company']}
Context: {achievement['context']}
Metrics: {achievement['metrics']}
Scope: {achievement['scope']}
Methods Used: {achievement['methods']}"""

        entries.append({
            "content": achievement_entry,
            "tags": ["achievement", achievement["company"].replace(" ", "_").lower(), "metrics", "quantifiable"]
        })

    # Skills with evidence
    for skill_data in data["skills"]:
        skill_entry = f"""SKILL: {skill_data['skill']}

Evidence:
{chr(10).join('- ' + e for e in skill_data['evidence'])}

Context: {skill_data.get('context', 'Multiple roles and companies')}"""

        if "tools" in skill_data:
            skill_entry += f"\n\nTools: {', '.join(skill_data['tools'])}"

        entries.append({
            "content": skill_entry,
            "tags": ["skill", skill_data["skill"].lower().replace(" ", "_"), "evidence"]
        })

    # Education
    edu = data["education"]
    entries.append({
        "content": f"""EDUCATION: {edu['degree']}
School: {edu['school']}
Location: {edu['location']}
Dates: {edu['dates']}""",
        "tags": ["education", "background"]
    })

    # Certifications
    for cert in data["certifications"]:
        entries.append({
            "content": f"CERTIFICATION: {cert}",
            "tags": ["certification", "pragmatic_marketing"]
        })

    # Writing style patterns
    style = data["writing_style"]
    entries.append({
        "content": f"""WRITING STYLE - Cover Letter Structure:
{chr(10).join('- ' + s for s in style['cover_letter_structure'])}

Tone Patterns:
{chr(10).join('- ' + t for t in style['tone_patterns'])}

Common Phrases:
{chr(10).join('- "' + p + '"' for p in style['common_phrases'])}

Opening Styles:
{chr(10).join('- ' + o for o in style['opening_styles'])}

Requirement Mapping Style: {style['requirement_mapping_style']}""",
        "tags": ["writing_style", "cover_letter", "tone"]
    })

    # Cover letter examples
    for example in data["cover_letter_examples"]:
        example_entry = f"""COVER LETTER EXAMPLE - {example['company']}

Opening: "{example['opening']}"

Closing: "{example.get('closing', '')}"
"""
        if "themes" in example:
            example_entry += f"\nThemes: {', '.join(example['themes'])}"
        if "structure_notes" in example:
            example_entry += f"\nStructure Notes: {example['structure_notes']}"

        entries.append({
            "content": example_entry,
            "tags": ["cover_letter_example", "writing_sample", example["company"].lower()]
        })

    return entries


if __name__ == "__main__":
    print("Career data structured and ready for supermemory import.")
    print(f"\nTotal entries to import: {len(format_for_supermemory(CAREER_DATA))}")
    print("\nCategories:")
    print(f"  - Personal values/stories: {len(CAREER_DATA['personal_values'])}")
    print(f"  - Job history entries: {len(CAREER_DATA['job_history'])}")
    print(f"  - Achievements: {len(CAREER_DATA['achievements'])}")
    print(f"  - Skills: {len(CAREER_DATA['skills'])}")
    print(f"  - Certifications: {len(CAREER_DATA['certifications'])}")
    print(f"  - Writing style patterns: 1")
    print(f"  - Cover letter examples: {len(CAREER_DATA['cover_letter_examples'])}")

    # Show sample entry
    entries = format_for_supermemory(CAREER_DATA)
    print("\n" + "="*60)
    print("SAMPLE ENTRY (Achievement):")
    print("="*60)
    sample = [e for e in entries if "ACHIEVEMENT" in e["content"]][0]
    print(sample["content"])
    print(f"\nTags: {', '.join(sample['tags'])}")
