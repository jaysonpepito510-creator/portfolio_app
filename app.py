from flask import Flask, jsonify, render_template_string, request, url_for
import json
import os
from werkzeug.utils import secure_filename
import time
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# Configure Cloudinary (Reads from environment variables set in Render/Railway)
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "your_cloud_name"),
    api_key=os.getenv("CLOUDINARY_API_KEY", "your_api_key"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", "your_api_secret"),
    secure=True
)

# Configure 50MB max upload limit
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

DATA_FILE = "portfolio_data.json"
MESSAGES_FILE = "contact_messages.json"

DEFAULT_PORTFOLIO = {
    "profile": {
        "fullName": "Jayson Pepito",
        "heroRole": "IT Specialist / Web Developer",
        "heroTagline": "Building enterprise-grade web applications, automated Python systems, and scalable databases for businesses in Maramag, Bukidnon and remote global teams.",
        "locationBadge": "📍 Maramag Bukidnon, Philippines • Available for Local & Remote Roles",
        "avatarUrl": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80",
        "aboutParagraph1": "I am a dedicated IT Specialist and Full-Stack Developer residing in Maramag, Bukidnon, Philippines. I specialize in bridging the gap between business operations and technological solutions—building fast, reliable, and user-friendly software systems.",
        "aboutParagraph2": "My core technical stack includes Python, Flask, MySQL, React, Vite, and Tailwind CSS. Beyond web development, my background encompasses network administration, computer hardware repair, database optimization, and deployment workflows.",
        "aboutParagraph3": "Driven by Mindanao's burgeoning tech industry, I am committed to delivering clean, maintainable code and exceptional technical support for local organizations as well as international remote enterprises.",
        "contactTagline": "Interested in collaborating on a web project, hiring an IT Specialist, or remote software engineering roles? Send me a message!",
        "email": "jayson.pepito.dev@gmail.com",
        "location": "Davao City, Davao del Sur, Philippines PH",
        "github": "https://github.com",
        "linkedin": "https://linkedin.com"
    },
    "projects": [
        {
            "id": "p1",
            "title": "AquaFlow — Water Refilling Station Dashboard",
            "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop&q=80",
            "description": "A full-stack web dashboard managing container inventory, delivery routes, customer billing logs, and daily revenue reporting for water refilling stations.",
            "tech": ["React", "Vite", "Tailwind CSS", "Flask", "MySQL"],
            "demo": "https://example.com",
            "github": "https://github.com"
        },
        {
            "id": "p2",
            "title": "My AI Assistant Application",
            "image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80",
            "description": "A Python desktop assistant with NLP capabilities, desktop command automation, API integrations, and instant web research query handlers.",
            "tech": ["Python 3", "CustomTkinter", "REST APIs", "NLP"],
            "demo": "https://example.com",
            "github": "https://github.com"
        }
    ],
    "awards": [
        {
            "id": "a1",
            "title": "Certified Full-Stack Developer",
            "issuer": "DICT Philippines / Tech Certification",
            "date": "2025",
            "category": "Certification",
            "image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&auto=format&fit=crop&q=80",
            "description": "Validated competencies in web development, database management, and cloud application deployment."
        }
    ],
    "timeline": [
        {
            "id": "t1",
            "role": "Freelance Full-Stack Developer",
            "organization": "Bukidnon & Remote Clients",
            "period": "2023 — Present",
            "description": "Delivered responsive web apps, RESTful APIs in Flask, and MySQL database optimizations."
        }
    ]
}


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_PORTFOLIO


def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    return jsonify(load_data())


@app.route('/api/portfolio', methods=['POST'])
def update_portfolio():
    data = request.json
    if data:
        save_data(data)
        return jsonify({"status": "success", "message": "Saved successfully!"})
    return jsonify({"status": "error", "message": "Invalid data"}), 400


@app.route('/api/contact', methods=['POST'])
def submit_contact():
    data = request.json
    if not data or not data.get('name') or not data.get('email') or not data.get('message'):
        return jsonify({"status": "error", "message": "Please fill in all required fields."}), 400

    messages = []
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r') as f:
                messages = json.load(f)
        except:
            messages = []

    data['timestamp'] = int(time.time())
    messages.append(data)

    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=4)

    return jsonify({"status": "success", "message": "Your message has been sent successfully!"})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    try:
        # Upload image directly to Cloudinary cloud storage
        upload_result = cloudinary.uploader.upload(file, folder="portfolio_uploads")
        file_url = upload_result.get("secure_url")
        return jsonify({"status": "success", "url": file_url})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/')
def index():
    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jayson Pepito | Interactive Editable Portfolio & CMS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        navy: { 950: '#070a12', 900: '#0b0f19', 850: '#111827', 800: '#1f2937', 700: '#374151' },
                        accent: { teal: '#0d9488', tealLight: '#14b8a6', cyan: '#06b6d4', emerald: '#10b981', blue: '#3b82f6' }
                    },
                    fontFamily: { sans: ['Inter', 'sans-serif'], mono: ['Fira Code', 'monospace'] }
                }
            }
        }
    </script>
    <style>
        body { background-color: #0b0f19; color: #f1f5f9; font-family: 'Inter', sans-serif; overflow-x: hidden; }
        .glass-panel { background: rgba(17, 24, 39, 0.85); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .glass-card { background: rgba(17, 24, 39, 0.5); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.06); transition: all 0.3s ease; }
        .glass-card:hover { border-color: rgba(6, 182, 212, 0.3); transform: translateY(-4px); }
        .text-gradient { background: linear-gradient(135deg, #14b8a6 0%, #06b6d4 50%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .btn-gradient { background: linear-gradient(135deg, #0d9488 0%, #06b6d4 100%); color: #fff; font-weight: 600; transition: all 0.3s ease; }
        .btn-gradient:hover { box-shadow: 0 0 20px rgba(13, 148, 136, 0.5); transform: translateY(-2px); }
        .edit-highlight { outline: 2px dashed #06b6d4; outline-offset: 4px; background-color: rgba(6, 182, 212, 0.05) !important; border-radius: 8px; }
    </style>
</head>
<body class="relative antialiased selection:bg-accent-cyan selection:text-navy-950">
    <div class="fixed top-0 left-1/4 w-96 h-96 bg-accent-teal/10 rounded-full blur-3xl pointer-events-none -z-10"></div>
    <div class="fixed bottom-10 right-10 w-96 h-96 bg-accent-blue/10 rounded-full blur-3xl pointer-events-none -z-10"></div>

    <!-- Edit Mode Bar -->
    <div class="fixed bottom-5 right-5 z-40 glass-panel p-3 rounded-2xl shadow-2xl border border-accent-cyan/30 flex flex-wrap items-center gap-3">
        <div class="flex items-center space-x-2 border-r border-white/10 pr-3">
            <span class="text-xs font-mono text-slate-300 font-medium">EDIT MODE</span>
            <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" id="edit-mode-toggle" onchange="handleEditModeToggle()" class="sr-only peer">
                <div class="w-11 h-6 bg-slate-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent-teal"></div>
            </label>
        </div>
        <div id="cms-actions" class="hidden flex flex-wrap items-center gap-2">
            <button onclick="saveAllChanges()" class="px-3 py-1.5 rounded-xl bg-accent-teal text-xs font-semibold text-white">Save</button>
            <button onclick="exportJSON()" class="px-3 py-1.5 rounded-xl bg-slate-800 text-xs text-slate-200 border border-white/10">Export</button>
            <label class="px-3 py-1.5 rounded-xl bg-slate-800 text-xs text-slate-200 border border-white/15 cursor-pointer">
                Import <input type="file" accept=".json" onchange="importJSON(event)" class="hidden">
            </label>
            <button onclick="resetDefaultData()" class="px-3 py-1.5 rounded-xl bg-red-500/10 text-xs text-red-400 border border-red-500/20">Reset</button>
        </div>
    </div>

    <!-- Header -->
    <header class="fixed top-0 left-0 w-full z-40 glass-panel border-b border-white/5">
        <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
            <a href="#hero" class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-teal to-accent-cyan flex items-center justify-center text-white font-bold font-mono text-xl">JP</div>
                <span class="text-lg font-bold text-white" id="nav-name">Jayson Pepito</span>
            </a>
            <nav class="hidden md:flex items-center space-x-8">
                <a href="#about" class="text-sm font-medium text-slate-300 hover:text-accent-teal">About</a>
                <a href="#skills" class="text-sm font-medium text-slate-300 hover:text-accent-teal">Skills</a>
                <a href="#projects" class="text-sm font-medium text-slate-300 hover:text-accent-teal">Projects</a>
                <a href="#awards" class="text-sm font-medium text-slate-300 hover:text-accent-teal">Awards</a>
                <a href="#experience" class="text-sm font-medium text-slate-300 hover:text-accent-teal">Timeline</a>
                <a href="#contact" class="text-sm font-medium text-slate-300 hover:text-accent-teal">Contact</a>
            </nav>
        </div>
    </header>

    <main class="pt-20">
        <!-- Hero Section -->
        <section id="hero" class="min-h-[calc(100vh-5rem)] flex items-center justify-center py-16 px-6 text-center">
            <div class="max-w-5xl mx-auto space-y-8">
                <div class="relative w-40 h-40 mx-auto group">
                    <img id="hero-avatar" src="" alt="Profile" class="w-full h-full rounded-full object-cover border-4 border-accent-teal/40 shadow-2xl">
                    <button onclick="openAvatarModal()" id="avatar-edit-btn" class="hidden absolute bottom-1 right-1 p-2 rounded-full bg-accent-cyan text-navy-950 shadow-lg hover:scale-110 transition-transform"><i data-lucide="camera" class="w-4 h-4"></i></button>
                </div>
                <div class="inline-flex items-center space-x-2 px-4 py-2 rounded-full glass-card text-sm font-medium text-accent-teal border border-accent-teal/25">
                    <span class="editable-field" data-key="locationBadge">📍 Maramag Bukidnon, Philippines</span>
                </div>
                <h1 class="text-5xl sm:text-7xl font-extrabold text-white">Hi, I'm <span class="text-gradient editable-field" data-key="fullName" id="hero-fullname">Jayson Pepito</span></h1>
                <p class="text-2xl text-slate-300 editable-field" data-key="heroRole">IT Specialist / Full-Stack Developer</p>
                <p class="text-lg text-slate-400 max-w-2xl mx-auto editable-field" data-key="heroTagline">Building enterprise-grade web applications and Python systems.</p>
            </div>
        </section>

        <!-- Projects Section -->
        <section id="projects" class="py-20 px-6 border-t border-white/5">
            <div class="max-w-6xl mx-auto">
                <div class="flex justify-between items-center mb-12">
                    <h2 class="text-3xl font-bold text-white">Featured Projects</h2>
                    <button onclick="openProjectModal(null)" id="add-project-btn" class="hidden btn-gradient px-4 py-2 rounded-xl text-xs font-semibold">+ Add Project</button>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8" id="projects-container"></div>
            </div>
        </section>

        <!-- Awards Section -->
        <section id="awards" class="py-20 px-6 border-t border-white/5">
            <div class="max-w-6xl mx-auto">
                <div class="flex justify-between items-center mb-12">
                    <h2 class="text-3xl font-bold text-white">Awards & Certifications</h2>
                    <button onclick="openAwardModal(null)" id="add-award-btn" class="hidden btn-gradient px-4 py-2 rounded-xl text-xs font-semibold">+ Add Award</button>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6" id="awards-container"></div>
            </div>
        </section>

        <!-- Timeline Section -->
        <section id="experience" class="py-20 px-6 border-t border-white/5">
            <div class="max-w-4xl mx-auto">
                <div class="flex justify-between items-center mb-12">
                    <h2 class="text-3xl font-bold text-white">Timeline</h2>
                    <button onclick="openTimelineModal(null)" id="add-timeline-btn" class="hidden btn-gradient px-4 py-2 rounded-xl text-xs font-semibold">+ Add Entry</button>
                </div>
                <div class="relative border-l border-white/10 ml-6 space-y-8" id="timeline-container"></div>
            </div>
        </section>

        <!-- Get In Touch Section -->
        <section id="contact" class="py-20 px-6 border-t border-white/5">
            <div class="max-w-6xl mx-auto">
                <div class="flex items-center space-x-3 mb-10">
                    <h2 class="text-4xl font-extrabold text-white">Get In Touch</h2>
                    <div class="flex-grow h-[1px] bg-gradient-to-r from-white/10 to-transparent ml-4"></div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
                    <!-- Left Column: Tagline & Info Cards -->
                    <div class="lg:col-span-5 space-y-6">
                        <p class="text-slate-300 text-lg leading-relaxed editable-field" data-key="contactTagline">
                            Interested in collaborating on a web project, hiring an IT Specialist, or remote software engineering roles? Send me a message!
                        </p>

                        <div class="space-y-4 pt-2">
                            <!-- Email Card -->
                            <div class="glass-card p-4 rounded-2xl flex items-center space-x-4 border border-white/5 hover:border-accent-cyan/30 transition-all">
                                <div class="w-12 h-12 rounded-xl bg-navy-900 border border-white/10 flex items-center justify-center text-accent-cyan shrink-0">
                                    <i data-lucide="mail" class="w-5 h-5"></i>
                                </div>
                                <div class="overflow-hidden">
                                    <span class="text-[11px] font-mono uppercase tracking-wider text-slate-400 block">Email</span>
                                    <a id="contact-email-link" href="mailto:jayson.pepito.dev@gmail.com" class="text-white font-mono font-medium text-sm hover:text-accent-cyan transition-colors truncate block editable-field" data-key="email">
                                        jayson.pepito.dev@gmail.com
                                    </a>
                                </div>
                            </div>

                            <!-- Location Card -->
                            <div class="glass-card p-4 rounded-2xl flex items-center space-x-4 border border-white/5 hover:border-accent-cyan/30 transition-all">
                                <div class="w-12 h-12 rounded-xl bg-navy-900 border border-white/10 flex items-center justify-center text-accent-teal shrink-0">
                                    <i data-lucide="map-pin" class="w-5 h-5"></i>
                                </div>
                                <div>
                                    <span class="text-[11px] font-mono uppercase tracking-wider text-slate-400 block">Location</span>
                                    <div class="text-white font-bold text-sm editable-field" data-key="location">
                                        Davao City, Davao del Sur, Philippines <span class="text-xs text-slate-400 font-mono font-normal">PH</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Social Icon Links -->
                        <div class="flex items-center space-x-3 pt-2">
                            <a id="github-link" href="https://github.com" target="_blank" rel="noopener noreferrer" class="w-10 h-10 rounded-xl glass-card flex items-center justify-center text-slate-300 hover:text-accent-cyan hover:border-accent-cyan/40 transition-all">
                                <i data-lucide="github" class="w-5 h-5"></i>
                            </a>
                            <a id="linkedin-link" href="https://linkedin.com" target="_blank" rel="noopener noreferrer" class="w-10 h-10 rounded-xl glass-card flex items-center justify-center text-slate-300 hover:text-accent-cyan hover:border-accent-cyan/40 transition-all">
                                <i data-lucide="linkedin" class="w-5 h-5"></i>
                            </a>
                        </div>
                    </div>

                    <!-- Right Column: Send Message Form -->
                    <div class="lg:col-span-7">
                        <div class="glass-panel p-8 rounded-3xl border border-white/10 shadow-2xl relative overflow-hidden">
                            <h3 class="text-2xl font-bold text-white mb-6">Send Message</h3>

                            <form onsubmit="submitContactForm(event)" class="space-y-5">
                                <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                                    <div>
                                        <label class="block text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-2">YOUR NAME</label>
                                        <input type="text" id="cf-name" required placeholder="Juan Dela Cruz" class="w-full bg-navy-950/80 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-accent-cyan transition-colors">
                                    </div>
                                    <div>
                                        <label class="block text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-2">YOUR EMAIL</label>
                                        <input type="email" id="cf-email" required placeholder="juan@example.com" class="w-full bg-navy-950/80 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-accent-cyan transition-colors">
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-2">MESSAGE</label>
                                    <textarea id="cf-message" rows="5" required placeholder="Write your message here..." class="w-full bg-navy-950/80 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-accent-cyan transition-colors resize-none"></textarea>
                                </div>

                                <button type="submit" id="cf-submit-btn" class="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-accent-teal to-accent-cyan text-navy-950 font-bold text-base hover:opacity-90 transition-all shadow-lg shadow-accent-cyan/20 active:scale-[0.99]">
                                    Submit Inquiry
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <!-- Password Modal -->
    <div id="password-modal" class="fixed inset-0 z-50 hidden bg-navy-950/80 backdrop-blur-md flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-sm rounded-3xl p-6 border border-white/15 space-y-4">
            <h3 class="font-bold text-white text-lg">Admin Authentication</h3>
            <form onsubmit="submitPasswordPrompt(event)" class="space-y-4">
                <input type="password" id="cms-password-input" required placeholder="Password" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white">
                <div class="flex justify-end space-x-3">
                    <button type="button" onclick="cancelPasswordPrompt()" class="text-xs text-slate-400">Cancel</button>
                    <button type="submit" class="btn-gradient px-5 py-2 rounded-xl text-xs font-semibold">Authenticate</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Project Modal -->
    <div id="project-modal" class="fixed inset-0 z-50 hidden bg-navy-950/80 backdrop-blur-md flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-lg rounded-3xl p-6 border border-white/15 space-y-4 max-h-[90vh] overflow-y-auto">
            <h3 id="project-modal-title" class="font-bold text-white text-lg">Add/Edit Project</h3>
            <form onsubmit="saveProjectForm(event)" class="space-y-4">
                <input type="hidden" id="pm-id">
                <input type="text" id="pm-title" required placeholder="Project Title" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white">
                <div>
                    <label class="block text-xs text-slate-400 mb-1">PROJECT IMAGE (Max 50MB)</label>
                    <input type="file" id="pm-file" accept="image/*" class="w-full bg-navy-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-300">
                    <input type="hidden" id="pm-image">
                </div>
                <textarea id="pm-desc" rows="3" required placeholder="Description" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white"></textarea>
                <input type="text" id="pm-tech" placeholder="Tech stack (comma-separated)" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white">
                <input type="text" id="pm-demo" placeholder="Demo URL" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white">
                <input type="text" id="pm-github" placeholder="GitHub URL" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white">
                <div class="flex justify-end space-x-3">
                    <button type="button" onclick="closeProjectModal()" class="text-xs text-slate-400">Cancel</button>
                    <button type="submit" class="btn-gradient px-5 py-2 rounded-xl text-xs font-semibold">Save Project</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Award Modal -->
    <div id="award-modal" class="fixed inset-0 z-50 hidden bg-navy-950/80 backdrop-blur-md flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-md rounded-3xl p-6 border border-white/15 space-y-4 max-h-[90vh] overflow-y-auto">
            <h3 class="font-bold text-white text-lg">Add/Edit Award</h3>
            <form onsubmit="saveAwardForm(event)" class="space-y-4">
                <input type="hidden" id="am-id">
                <input type="text" id="am-title" required placeholder="Award Title" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white">
                <input type="text" id="am-issuer" required placeholder="Issuer" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white">
                <div>
                    <label class="block text-xs text-slate-400 mb-1">CERTIFICATE / AWARD IMAGE (Max 50MB)</label>
                    <input type="file" id="am-file" accept="image/*" class="w-full bg-navy-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-300">
                    <input type="hidden" id="am-image">
                </div>
                <input type="text" id="am-date" placeholder="Year" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white">
                <input type="text" id="am-category" placeholder="Category" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white">
                <textarea id="am-desc" rows="2" placeholder="Description" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white"></textarea>
                <div class="flex justify-end space-x-3">
                    <button type="button" onclick="closeAwardModal()" class="text-xs text-slate-400">Cancel</button>
                    <button type="submit" class="btn-gradient px-5 py-2 rounded-xl text-xs font-semibold">Save Award</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Timeline Modal -->
    <div id="timeline-modal" class="fixed inset-0 z-50 hidden bg-navy-950/80 backdrop-blur-md flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-md rounded-3xl p-6 border border-white/15 space-y-4">
            <h3 class="font-bold text-white text-lg">Add/Edit Timeline</h3>
            <form onsubmit="saveTimelineForm(event)" class="space-y-4">
                <input type="hidden" id="tm-id">
                <input type="text" id="tm-role" required placeholder="Role / Degree" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white">
                <input type="text" id="tm-org" required placeholder="Organization" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white">
                <input type="text" id="tm-period" placeholder="Period (e.g. 2023 - Present)" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white">
                <textarea id="tm-desc" rows="2" placeholder="Description" class="w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-white"></textarea>
                <div class="flex justify-end space-x-3">
                    <button type="button" onclick="closeTimelineModal()" class="text-xs text-slate-400">Cancel</button>
                    <button type="submit" class="btn-gradient px-5 py-2 rounded-xl text-xs font-semibold">Save Entry</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Avatar Modal -->
    <div id="avatar-modal" class="fixed inset-0 z-50 hidden bg-navy-950/80 backdrop-blur-md flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-sm rounded-3xl p-6 border border-white/15 space-y-4">
            <h3 class="font-bold text-white text-lg">Update Profile Picture (Max 50MB)</h3>
            <input type="file" id="avatar-file" accept="image/*" class="w-full bg-navy-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-300">
            <div class="flex justify-end space-x-3">
                <button onclick="closeAvatarModal()" class="text-xs text-slate-400">Cancel</button>
                <button onclick="uploadAvatarPhoto()" class="btn-gradient px-5 py-2 rounded-xl text-xs font-semibold">Upload & Apply</button>
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div id="toast" class="fixed bottom-6 left-6 z-50 transform -translate-y-10 opacity-0 transition-all duration-300 pointer-events-none glass-panel border border-accent-teal/40 px-5 py-3 rounded-2xl text-sm font-medium text-white shadow-2xl"></div>

    <script>
        const EDIT_MODE_PASSWORD = "Jayson200316";
        let appData = {};
        let isEditMode = false;

        async function fetchPortfolioData() {
            const res = await fetch('/api/portfolio');
            appData = await res.json();
            renderPortfolio();
        }

        window.onload = function() {
            fetchPortfolioData();
            lucide.createIcons();
        };

        function renderPortfolio() {
            document.querySelectorAll('.editable-field').forEach(el => {
                const key = el.dataset.key;
                if (appData.profile && appData.profile[key] !== undefined) {
                    el.textContent = appData.profile[key];
                }
            });
            if (appData.profile) {
                document.getElementById('nav-name').textContent = appData.profile.fullName || "";
                document.getElementById('hero-fullname').textContent = appData.profile.fullName || "";
                if (appData.profile.avatarUrl) document.getElementById('hero-avatar').src = appData.profile.avatarUrl;
                if (appData.profile.email) document.getElementById('contact-email-link').href = `mailto:${appData.profile.email}`;
                if (appData.profile.github) document.getElementById('github-link').href = appData.profile.github;
                if (appData.profile.linkedin) document.getElementById('linkedin-link').href = appData.profile.linkedin;
            }
            renderProjects();
            renderAwards();
            renderTimeline();
            lucide.createIcons();
        }

        function renderProjects() {
            const container = document.getElementById('projects-container');
            if (!container) return;
            container.innerHTML = '';
            (appData.projects || []).forEach(p => {
                const div = document.createElement('div');
                div.className = 'glass-card rounded-3xl overflow-hidden p-6 space-y-3 relative';
                div.innerHTML = `
                    ${isEditMode ? `
                        <div class="absolute top-4 right-4 flex space-x-2 z-10">
                            <button onclick="openProjectModal('${p.id}')" class="p-2 rounded-xl bg-accent-cyan text-navy-950 font-bold shadow"><i data-lucide="edit-3" class="w-4 h-4"></i></button>
                            <button onclick="deleteProject('${p.id}')" class="p-2 rounded-xl bg-red-500 text-white font-bold shadow"><i data-lucide="trash-2" class="w-4 h-4"></i></button>
                        </div>
                    ` : ''}
                    <img src="${p.image}" class="w-full h-48 object-cover rounded-xl">
                    <h3 class="text-xl font-bold text-white">${p.title}</h3>
                    <p class="text-xs text-slate-300">${p.description}</p>
                    <div class="flex flex-wrap gap-1.5 pt-2">
                        ${(p.tech || []).map(t => `<span class="text-[10px] font-mono px-2 py-0.5 rounded-md bg-navy-950 text-accent-cyan border border-white/5">${t}</span>`).join('')}
                    </div>
                `;
                container.appendChild(div);
            });
        }

        function renderAwards() {
            const container = document.getElementById('awards-container');
            if (!container) return;
            container.innerHTML = '';
            (appData.awards || []).forEach(a => {
                const div = document.createElement('div');
                div.className = 'glass-card rounded-3xl overflow-hidden p-6 space-y-3 relative flex flex-col justify-between';
                div.innerHTML = `
                    ${isEditMode ? `
                        <div class="absolute top-4 right-4 flex space-x-2 z-10">
                            <button onclick="openAwardModal('${a.id}')" class="p-2 rounded-xl bg-accent-cyan text-navy-950 font-bold shadow"><i data-lucide="edit-3" class="w-4 h-4"></i></button>
                            <button onclick="deleteAward('${a.id}')" class="p-2 rounded-xl bg-red-500 text-white font-bold shadow"><i data-lucide="trash-2" class="w-4 h-4"></i></button>
                        </div>
                    ` : ''}
                    <div>
                        ${a.image ? `<img src="${a.image}" class="w-full h-40 object-cover rounded-xl mb-4">` : ''}
                        <h3 class="font-bold text-white text-lg">${a.title}</h3>
                        <div class="text-xs text-accent-cyan mt-1">${a.issuer} (${a.date})</div>
                        <p class="text-xs text-slate-300 mt-2">${a.description}</p>
                    </div>
                `;
                container.appendChild(div);
            });
        }

        function renderTimeline() {
            const container = document.getElementById('timeline-container');
            if (!container) return;
            container.innerHTML = '';
            (appData.timeline || []).forEach(t => {
                const div = document.createElement('div');
                div.className = 'relative pl-6';
                div.innerHTML = `
                    <div class="glass-card p-6 rounded-2xl space-y-2 relative">
                        ${isEditMode ? `
                            <div class="absolute top-4 right-4 flex space-x-1 z-10">
                                <button onclick="openTimelineModal('${t.id}')" class="p-1.5 rounded-lg bg-accent-cyan text-navy-950"><i data-lucide="edit-3" class="w-3.5 h-3.5"></i></button>
                                <button onclick="deleteTimeline('${t.id}')" class="p-1.5 rounded-lg bg-red-500 text-white"><i data-lucide="trash-2" class="w-3.5 h-3.5"></i></button>
                            </div>
                        ` : ''}
                        <h3 class="text-lg font-bold text-white">${t.role}</h3>
                        <p class="text-xs text-slate-400">${t.organization} (${t.period})</p>
                        <p class="text-xs text-slate-300">${t.description}</p>
                    </div>
                `;
                container.appendChild(div);
            });
        }

        async function submitContactForm(e) {
            e.preventDefault();
            const btn = document.getElementById('cf-submit-btn');
            btn.disabled = true;
            btn.textContent = 'Sending...';

            const payload = {
                name: document.getElementById('cf-name').value,
                email: document.getElementById('cf-email').value,
                message: document.getElementById('cf-message').value
            };

            try {
                const res = await fetch('/api/contact', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.status === 'success') {
                    showToast(data.message);
                    document.getElementById('cf-name').value = '';
                    document.getElementById('cf-email').value = '';
                    document.getElementById('cf-message').value = '';
                } else {
                    alert(data.message || 'Error submitting message.');
                }
            } catch (err) {
                alert('An error occurred. Please try again.');
            } finally {
                btn.disabled = false;
                btn.textContent = 'Submit Inquiry';
            }
        }

        function handleEditModeToggle() {
            const toggle = document.getElementById('edit-mode-toggle');
            if (toggle.checked && !isEditMode) {
                toggle.checked = false;
                document.getElementById('password-modal').classList.remove('hidden');
            } else if (!toggle.checked && isEditMode) {
                saveAllChanges();
            }
        }

        function submitPasswordPrompt(e) {
            e.preventDefault();
            if (document.getElementById('cms-password-input').value === EDIT_MODE_PASSWORD) {
                document.getElementById('password-modal').classList.add('hidden');
                document.getElementById('edit-mode-toggle').checked = true;
                isEditMode = true;
                document.getElementById('cms-actions').classList.remove('hidden');
                document.getElementById('avatar-edit-btn').classList.remove('hidden');
                document.getElementById('add-project-btn').classList.remove('hidden');
                document.getElementById('add-award-btn').classList.remove('hidden');
                document.getElementById('add-timeline-btn').classList.remove('hidden');
                makeFieldsEditable(true);
                renderPortfolio();
                showToast("Edit Mode Activated!");
            } else {
                alert("Incorrect password.");
            }
        }

        function cancelPasswordPrompt() {
            document.getElementById('password-modal').classList.add('hidden');
            document.getElementById('edit-mode-toggle').checked = false;
        }

        function makeFieldsEditable(enable) {
            document.querySelectorAll('.editable-field').forEach(el => {
                el.contentEditable = enable ? "true" : "false";
                if (enable) el.classList.add('edit-highlight');
                else el.classList.remove('edit-highlight');
            });
        }

        async function saveAllChanges() {
            document.querySelectorAll('.editable-field').forEach(el => {
                const key = el.dataset.key;
                if (key && appData.profile) appData.profile[key] = el.textContent.trim();
            });
            await syncWithServer();
            isEditMode = false;
            document.getElementById('edit-mode-toggle').checked = false;
            document.getElementById('cms-actions').classList.add('hidden');
            document.getElementById('avatar-edit-btn').classList.add('hidden');
            document.getElementById('add-project-btn').classList.add('hidden');
            document.getElementById('add-award-btn').classList.add('hidden');
            document.getElementById('add-timeline-btn').classList.add('hidden');
            makeFieldsEditable(false);
            renderPortfolio();
            showToast("Saved successfully!");
        }

        async function syncWithServer() {
            await fetch('/api/portfolio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(appData)
            });
        }

        async function uploadFile(fileInputId) {
            const fileInput = document.getElementById(fileInputId);
            if (fileInput.files.length > 0) {
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                const res = await fetch('/api/upload', { method: 'POST', body: formData });
                const data = await res.json();
                if (data.status === 'success') return data.url;
            }
            return null;
        }

        // Project CRUD
        function openProjectModal(id) {
            document.getElementById('project-modal').classList.remove('hidden');
            if (id) {
                const p = appData.projects.find(x => x.id === id);
                document.getElementById('pm-id').value = p.id;
                document.getElementById('pm-title').value = p.title;
                document.getElementById('pm-image').value = p.image;
                document.getElementById('pm-desc').value = p.description;
                document.getElementById('pm-tech').value = p.tech.join(', ');
                document.getElementById('pm-demo').value = p.demo;
                document.getElementById('pm-github').value = p.github;
            } else {
                document.getElementById('pm-id').value = '';
                document.getElementById('pm-title').value = '';
                document.getElementById('pm-image').value = 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop&q=80';
                document.getElementById('pm-file').value = '';
                document.getElementById('pm-desc').value = '';
                document.getElementById('pm-tech').value = '';
            }
        }
        function closeProjectModal() { document.getElementById('project-modal').classList.add('hidden'); }

        async function saveProjectForm(e) {
            e.preventDefault();
            let imageUrl = document.getElementById('pm-image').value;
            const uploadedUrl = await uploadFile('pm-file');
            if (uploadedUrl) imageUrl = uploadedUrl;

            const id = document.getElementById('pm-id').value;
            const tech = document.getElementById('pm-tech').value.split(',').map(s => s.trim()).filter(Boolean);
            const proj = {
                id: id || 'p_' + Date.now(),
                title: document.getElementById('pm-title').value,
                image: imageUrl,
                description: document.getElementById('pm-desc').value,
                tech: tech,
                demo: document.getElementById('pm-demo').value,
                github: document.getElementById('pm-github').value
            };

            if (!appData.projects) appData.projects = [];
            if (id) {
                const idx = appData.projects.findIndex(x => x.id === id);
                if (idx !== -1) appData.projects[idx] = proj;
            } else {
                appData.projects.push(proj);
            }
            await syncWithServer();
            closeProjectModal();
            renderPortfolio();
            showToast("Project saved!");
        }

        function deleteProject(id) {
            if (confirm("Delete project?")) {
                appData.projects = appData.projects.filter(x => x.id !== id);
                syncWithServer();
                renderPortfolio();
            }
        }

        // Award CRUD
        function openAwardModal(id) {
            document.getElementById('award-modal').classList.remove('hidden');
            if (id) {
                const a = appData.awards.find(x => x.id === id);
                document.getElementById('am-id').value = a.id;
                document.getElementById('am-title').value = a.title;
                document.getElementById('am-issuer').value = a.issuer;
                document.getElementById('am-image').value = a.image || '';
                document.getElementById('am-date').value = a.date;
                document.getElementById('am-category').value = a.category;
                document.getElementById('am-desc').value = a.description;
            } else {
                document.getElementById('am-id').value = '';
                document.getElementById('am-title').value = '';
                document.getElementById('am-issuer').value = '';
                document.getElementById('am-image').value = 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&auto=format&fit=crop&q=80';
                document.getElementById('am-date').value = '';
                document.getElementById('am-category').value = '';
                document.getElementById('am-desc').value = '';
            }
            document.getElementById('am-file').value = '';
        }

        function closeAwardModal() { document.getElementById('award-modal').classList.add('hidden'); }

        async function saveAwardForm(e) {
            e.preventDefault();
            const id = document.getElementById('am-id').value;
            let imageUrl = await uploadFile('am-file') || document.getElementById('am-image').value;

            const awardData = {
                id: id || 'a_' + Date.now(),
                title: document.getElementById('am-title').value,
                issuer: document.getElementById('am-issuer').value,
                image: imageUrl,
                date: document.getElementById('am-date').value,
                category: document.getElementById('am-category').value,
                description: document.getElementById('am-desc').value
            };
            if (!appData.awards) appData.awards = [];
            if (id) {
                const index = appData.awards.findIndex(x => x.id === id);
                if (index !== -1) appData.awards[index] = awardData;
            } else {
                appData.awards.push(awardData);
            }
            await syncWithServer();
            closeAwardModal();
            renderPortfolio();
            showToast("Award saved successfully!");
        }

        function deleteAward(id) {
            if (confirm("Delete award?")) {
                appData.awards = appData.awards.filter(x => x.id !== id);
                syncWithServer();
                renderPortfolio();
            }
        }

        // Timeline CRUD
        function openTimelineModal(id) {
            document.getElementById('timeline-modal').classList.remove('hidden');
            if (id) {
                const t = appData.timeline.find(x => x.id === id);
                document.getElementById('tm-id').value = t.id;
                document.getElementById('tm-role').value = t.role;
                document.getElementById('tm-org').value = t.organization;
                document.getElementById('tm-period').value = t.period;
                document.getElementById('tm-desc').value = t.description;
            } else {
                document.getElementById('tm-id').value = '';
                document.getElementById('tm-role').value = '';
                document.getElementById('tm-org').value = '';
                document.getElementById('tm-period').value = '';
                document.getElementById('tm-desc').value = '';
            }
        }
        function closeTimelineModal() { document.getElementById('timeline-modal').classList.add('hidden'); }

        async function saveTimelineForm(e) {
            e.preventDefault();
            const id = document.getElementById('tm-id').value;
            const entry = {
                id: id || 't_' + Date.now(),
                role: document.getElementById('tm-role').value,
                organization: document.getElementById('tm-org').value,
                period: document.getElementById('tm-period').value,
                description: document.getElementById('tm-desc').value
            };
            if (!appData.timeline) appData.timeline = [];
            if (id) {
                const idx = appData.timeline.findIndex(x => x.id === id);
                if (idx !== -1) appData.timeline[idx] = entry;
            } else {
                appData.timeline.push(entry);
            }
            await syncWithServer();
            closeTimelineModal();
            renderPortfolio();
            showToast("Timeline saved!");
        }

        function deleteTimeline(id) {
            if (confirm("Delete timeline entry?")) {
                appData.timeline = appData.timeline.filter(x => x.id !== id);
                syncWithServer();
                renderPortfolio();
            }
        }

        // Avatar Modal
        function openAvatarModal() { document.getElementById('avatar-modal').classList.remove('hidden'); }
        function closeAvatarModal() { document.getElementById('avatar-modal').classList.add('hidden'); }

        async function uploadAvatarPhoto() {
            const url = await uploadFile('avatar-file');
            if (url) {
                appData.profile.avatarUrl = url;
                await syncWithServer();
                closeAvatarModal();
                renderPortfolio();
                showToast("Profile picture updated!");
            } else {
                alert("Please select a valid image file.");
            }
        }

        function exportJSON() {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(appData, null, 2));
            const dl = document.createElement('a');
            dl.setAttribute("href", dataStr);
            dl.setAttribute("download", `portfolio_backup_${Date.now()}.json`);
            dl.click();
        }

        function importJSON(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = async function(e) {
                    try {
                        appData = JSON.parse(e.target.result);
                        await syncWithServer();
                        renderPortfolio();
                        showToast("Imported successfully!");
                    } catch (err) {
                        alert("Invalid JSON file.");
                    }
                };
                reader.readAsText(file);
            }
        }

        function resetDefaultData() {
            if (confirm("Reset to defaults?")) {
                fetch('/api/portfolio', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({{ default_portfolio | tojson }})
                }).then(() => fetchPortfolioData());
            }
        }

        function showToast(msg) {
            const toast = document.getElementById('toast');
            toast.textContent = msg;
            toast.classList.remove('-translate-y-10', 'opacity-0', 'pointer-events-none');
            setTimeout(() => toast.classList.add('-translate-y-10', 'opacity-0', 'pointer-events-none'), 3000);
        }
    </script>
</body>
</html>
"""
    return render_template_string(HTML_TEMPLATE, default_portfolio=DEFAULT_PORTFOLIO)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)