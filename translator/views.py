from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from translate import Translator  # Updated import
import os
import datetime

# Dictionary of common English to Tamil translations
TAMIL_COMMON_WORDS = {
    "mother": "அம்மா",
    "father": "அப்பா",
    "brother": "அண்ணன்",
    "sister": "அக்கா",
    "hello": "வணக்கம்",
    "thank you": "நன்றி",
    "yes": "ஆம்",
    "no": "இல்லை",
    "good": "நல்லது",
    "bad": "கெட்டது",
    "love": "அன்பு",
    "friend": "நண்பர்",
    "water": "தண்ணீர்",
    "food": "உணவு",
    "house": "வீடு",
    "car": "கார்",
    "book": "புத்தகம்",
    "school": "பள்ளி",
    "teacher": "ஆசிரியர்",
    "student": "மாணவர்",
    "morning": "காலை",
    "evening": "மாலை",
    "night": "இரவு",
    "today": "இன்று",
    "tomorrow": "நாளை",
    "yesterday": "நேற்று",
    "please": "தயவுசெய்து",
    "sorry": "மன்னிக்கவும்",
    "welcome": "வரவேற்கிறேன்",
    "goodbye": "பிரியாவிடை"
}

# Translation cache to improve performance
TRANSLATION_CACHE = {}
MAX_CACHE_SIZE = 100

# Translation history
HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'translation_history.json')

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

@csrf_exempt
def translate_text(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        language = request.POST.get('language', 'es')
        
        # Don't translate if text is empty
        if not text:
            return JsonResponse({'translated_text': ''})
        
        # Check cache first
        cache_key = f"{text}:{language}"
        if cache_key in TRANSLATION_CACHE:
            translated_text = TRANSLATION_CACHE[cache_key]
            print(f"Cache hit: '{translated_text}'")
            
            # Update history
            history = load_history()
            history.append({
                'original': text,
                'translated': translated_text,
                'language': language,
                'timestamp': datetime.datetime.now().isoformat()
            })
            if len(history) > 50:
                history = history[-50:]
            save_history(history)
            
            return JsonResponse({
                'translated_text': translated_text,
                'language_code': language,
                'detected_language': 'en',
                'source': 'cache'
            })
        
        # Check if it's Tamil and a common word we know
        if language == 'ta' and text.lower() in TAMIL_COMMON_WORDS:
            translated_text = TAMIL_COMMON_WORDS[text.lower()]
        else:
            # Split text into sentences for better translation of longer content
            sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
            
            # If it's a single word or short phrase, don't split
            if len(sentences) <= 1 or len(text.split()) <= 5:
                sentences = [text]
            
            translated_sentences = []
            
            for sentence in sentences:
                if not sentence:
                    continue
                    
                # For Tamil specifically, use the correct language code
                if language == 'ta':
                    # Create translator with specific settings for Tamil
                    translator = Translator(to_lang='ta', provider='mymemory')
                else:
                    translator = Translator(to_lang=language)
                    
                try:
                    translated_sentence = translator.translate(sentence)
                    
                    # Check if translation looks like it might be in the wrong language for Tamil
                    if language == 'ta' and not any(ord(c) >= 0x0B80 and ord(c) <= 0x0BFF for c in translated_sentence):
                        # Fallback to a more specific translation for Tamil
                        translator = Translator(to_lang='ta-IN', provider='mymemory')
                        translated_sentence = translator.translate(sentence)
                        
                    translated_sentences.append(translated_sentence)
                    
                except Exception as e:
                    print(f"Translation error for sentence '{sentence}': {str(e)}")
                    # If translation fails, keep the original sentence
                    translated_sentences.append(f"[Error translating: {sentence}]")
            
            # Join the translated sentences
            translated_text = '. '.join(translated_sentences)
            
            # Clean up the result
            translated_text = translated_text.replace('..', '.').replace('. .', '.').strip()
        
        # Update cache
        if len(TRANSLATION_CACHE) >= MAX_CACHE_SIZE:
            # Remove a random item if cache is full
            TRANSLATION_CACHE.pop(next(iter(TRANSLATION_CACHE)))
        TRANSLATION_CACHE[cache_key] = translated_text
        
        # Update history
        history = load_history()
        history.append({
            'original': text,
            'translated': translated_text,
            'language': language,
            'timestamp': datetime.datetime.now().isoformat()
        })
        # Keep only the last 50 translations
        if len(history) > 50:
            history = history[-50:]
        save_history(history)
        
        print(f"Translation result: '{translated_text}'")  # Debug log
        
        return JsonResponse({
            'translated_text': translated_text,
            'language_code': language,
            'detected_language': 'en',  # In a real app, you'd detect this
            'source': 'api'
        })
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'registration/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'registration/login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            return render(request, 'registration/signup.html', {'error': 'Passwords do not match'})
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('index')
        except Exception as e:
            return render(request, 'registration/signup.html', {'error': str(e)})
    
    return render(request, 'registration/signup.html')

@login_required
def index(request):
    # Get available languages for the dropdown
    languages = {
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'ta': 'Tamil',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ru': 'Russian',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'ko': 'Korean',
        'it': 'Italian',
        'pt': 'Portuguese',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'tr': 'Turkish',
        'pl': 'Polish',
        'vi': 'Vietnamese',
        'th': 'Thai',
        'id': 'Indonesian',
        'he': 'Hebrew',
        'bn': 'Bengali',
        'fa': 'Persian'
    }
    
    # Get recent translations
    history = load_history()[-5:]  # Last 5 translations
    
    return render(request, 'index.html', {
        'languages': languages,
        'history': history,
        'user': request.user  # Pass user information to template
    })

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('login')
    return redirect('login')

@csrf_exempt
def get_paginated_history(request):
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    
    history = load_history()
    
    # Calculate pagination
    total_items = len(history)
    total_pages = (total_items + page_size - 1) // page_size
    
    # Get the requested page
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)
    page_items = history[start_idx:end_idx]
    
    return JsonResponse({
        'history': page_items,
        'pagination': {
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'page_size': page_size
        }
    })

@csrf_exempt
def clear_history(request):
    if request.method == 'POST':
        save_history([])
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def delete_history_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            original = data.get('original')
            timestamp = data.get('timestamp')

            if not original or not timestamp:
                return JsonResponse({'error': 'Missing data'}, status=400)

            history = load_history()
            original_length = len(history)
            
            # Remove the matching item
            history = [
                item for item in history 
                if not (item['original'] == original and 
                       item['timestamp'].startswith(timestamp.strip()))
            ]

            if len(history) == original_length:
                return JsonResponse({'error': 'Item not found'}, status=404)

            save_history(history)
            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error deleting history item: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
def detect_language(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        
        if not text:
            return JsonResponse({'detected_language': 'unknown'})
        
        # Simple detection based on character sets
        try:
            if any(ord(c) >= 0x0B80 and ord(c) <= 0x0BFF for c in text):
                return JsonResponse({'detected_language': 'ta', 'confidence': 0.9})
            elif any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in text):
                return JsonResponse({'detected_language': 'hi', 'confidence': 0.9})
            elif any(ord(c) >= 0x0600 and ord(c) <= 0x06FF for c in text):
                return JsonResponse({'detected_language': 'ar', 'confidence': 0.9})
            elif any(ord(c) >= 0x4E00 and ord(c) <= 0x9FFF for c in text):
                return JsonResponse({'detected_language': 'zh', 'confidence': 0.9})
            elif any(ord(c) >= 0x3040 and ord(c) <= 0x30FF for c in text):
                return JsonResponse({'detected_language': 'ja', 'confidence': 0.9})
            elif any(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in text):
                return JsonResponse({'detected_language': 'ko', 'confidence': 0.9})
            else:
                # Default to English for Latin script
                return JsonResponse({'detected_language': 'en', 'confidence': 0.7})
        except Exception as e:
            print(f"Language detection error: {str(e)}")
            return JsonResponse({'detected_language': 'unknown', 'error': str(e)})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def get_history(request):
    history = load_history()
    return JsonResponse({'history': history})


@csrf_exempt
@require_http_methods(["POST"])
def translate_text(request):
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        target_language = data.get('target_language', '')

        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)
        if not target_language:
            return JsonResponse({'error': 'Target language is required'}, status=400)

        # Check Tamil common words first
        if target_language == 'ta' and text.lower() in TAMIL_COMMON_WORDS:
            translated_text = TAMIL_COMMON_WORDS[text.lower()]
        else:
            try:
                # Initialize translator with specific settings
                if target_language == 'ta':
                    translator = Translator(from_lang='en', to_lang='ta-IN')
                else:
                    translator = Translator(from_lang='en', to_lang=target_language)
                
                # Perform translation
                translated_text = translator.translate(text)
                
                # Verify Tamil translation
                if target_language == 'ta' and not any(ord(c) >= 0x0B80 and ord(c) <= 0x0BFF for c in translated_text):
                    # Fallback to dictionary if available
                    if text.lower() in TAMIL_COMMON_WORDS:
                        translated_text = TAMIL_COMMON_WORDS[text.lower()]
            except Exception as e:
                print(f"Translation error: {str(e)}")
                return JsonResponse({'error': 'Translation failed. Please try again.'}, status=500)

        # Update history
        history = load_history()
        history.append({
            'original': text,
            'translated': translated_text,
            'language': target_language,
            'timestamp': datetime.datetime.now().isoformat()
        })
        if len(history) > 50:
            history = history[-50:]
        save_history(history)

        return JsonResponse({
            'translated_text': translated_text,
            'target_language': target_language,
            'success': True
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request format'}, status=400)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
