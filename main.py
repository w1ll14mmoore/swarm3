import os
import random
import time
from swarm import Swarm, Agent
from swarm.repl import run_demo_loop
from serpapi import GoogleSearch
from colorama import Fore, Style, init
from tqdm import tqdm

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Ensure your OpenAI API key is set
openai_api_key = os.environ.get('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("Please set your OPENAI_API_KEY in the Secrets tab")

# Ensure your SerpApi key is set
serpapi_api_key = os.environ.get('SERPAPI_API_KEY')
if not serpapi_api_key:
    raise ValueError("Please set your SERPAPI_API_KEY in the Secrets tab")

class ChatHistory:
    def __init__(self):
        self.history = []

    def add(self, role, message):
        self.history.append({"role": role, "content": message})

    def get_last_n(self, n):
        return self.history[-n:]

chat_history = ChatHistory()

def print_colored(text, color):
    print(f"{color}{text}{Style.RESET_ALL}")

def simulate_progress(duration):
    for _ in tqdm(range(100), desc="Processing", ncols=70):
        time.sleep(duration / 100)

# Real-time internet search function using SerpApi
def internet_search(context_variables, query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": serpapi_api_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    organic_results = results.get("organic_results", [])[:3]
    formatted_results = []
    for result in organic_results:
        formatted_results.append(f"Title: {result['title']}\nLink: {result['link']}\nSnippet: {result['snippet']}\n")

    search_results = "\n".join(formatted_results)
    context_variables['last_research'] = search_results
    return search_results

# Other functions (keep these as they are)
def generate_ad_concept(context_variables, product, target_audience):
    research = context_variables.get('last_research', 'No research available')
    concept = f"Ad concept for {product} targeting {target_audience}: [Creative concept based on {research}]"
    context_variables['last_concept'] = concept
    return concept

def create_media_plan(context_variables, budget, duration):
    concept = context_variables.get('last_concept', 'No concept available')
    plan = f"Media plan with budget ${budget} for {duration} days: [Plan based on {concept}]"
    context_variables['last_media_plan'] = plan
    return plan

def social_media_strategy(context_variables, platforms):
    concept = context_variables.get('last_concept', 'No concept available')
    strategy = f"Social media strategy for {', '.join(platforms)}: [Strategy based on {concept}]"
    context_variables['last_social_strategy'] = strategy
    return strategy

def seo_optimization(context_variables, website, keywords):
    research = context_variables.get('last_research', 'No research available')
    optimization = f"SEO optimization for {website} focusing on {', '.join(keywords)}: [Optimization based on {research}]"
    context_variables['last_seo_optimization'] = optimization
    return optimization

def analyze_campaign(context_variables, campaign_id):
    plan = context_variables.get('last_media_plan', 'No media plan available')
    analysis = f"Analysis of campaign {campaign_id}: [Performance insights based on {plan}]"
    context_variables['last_analysis'] = analysis
    return analysis

# Define agents
nlp_agent = Agent(
    name="NLP Agent",
    instructions="""You are responsible for understanding and classifying user queries. 
    Determine if the query is an information request or a marketing plan request. 
    Extract key information from the query."""
)

research_agent = Agent(
    name="Research Agent",
    instructions="""You specialize in gathering and summarizing information. 
    Use the internet_search function to find relevant data and provide a comprehensive summary.""",
    functions=[internet_search]
)

creative_agent = Agent(
    name="Creative Agent",
    instructions="""Based on the research provided, generate compelling ad concepts and copy for the product or campaign.""",
    functions=[generate_ad_concept]
)

media_agent = Agent(
    name="Media Agent",
    instructions="""Develop a comprehensive media plan for the campaign or product launch.""",
    functions=[create_media_plan]
)

social_media_agent = Agent(
    name="Social Media Agent",
    instructions="""Create a social media strategy aligned with the overall campaign concept and target audience.""",
    functions=[social_media_strategy]
)

seo_agent = Agent(
    name="SEO Agent",
    instructions="""Develop an SEO strategy to improve search rankings for the product or campaign.""",
    functions=[seo_optimization, internet_search]
)

analytics_agent = Agent(
    name="Analytics Agent",
    instructions="""Develop a plan for measuring the success of the campaign or product launch.""",
    functions=[analyze_campaign]
)

summarization_agent = Agent(
    name="Summarization Agent",
    instructions="""Summarize and distill information from other agents into concise, relevant responses."""
)

class ImprovedProject:
    def __init__(self):
        self.query_type = None
        self.key_info = None
        self.research_data = None
        self.user_confirmation = False
        self.ad_concept = None
        self.media_plan = None
        self.social_strategy = None
        self.seo_plan = None
        self.analytics_plan = None

def parse_nlp_response(response):
    content = response.messages[-1]['content']
    if "information request" in content.lower():
        query_type = "information_request"
    elif "marketing plan" in content.lower():
        query_type = "marketing_plan"
    else:
        query_type = "unknown"

    key_info = content.split("Key Information:")[-1].strip()
    return query_type, key_info

def get_user_confirmation(query_type, key_info):
    print_colored(f"I understood your query as a {query_type}.", Fore.YELLOW)
    print_colored(f"Key information: {key_info}", Fore.YELLOW)
    confirmation = input(Fore.YELLOW + "Is this correct? (yes/no): " + Style.RESET_ALL).lower()
    return confirmation == 'yes'

def handle_information_request(client, project):
    print_colored("Researching your query...", Fore.CYAN)
    simulate_progress(2)  # Simulate 2 seconds of research
    research_response = client.run(research_agent, [{"role": "user", "content": project.key_info}])
    print_colored("Summarizing findings...", Fore.CYAN)
    simulate_progress(1)  # Simulate 1 second of summarization
    summarized_response = client.run(summarization_agent, [{"role": "user", "content": research_response.messages[-1]['content']}])
    return summarized_response.messages[-1]['content']

def handle_marketing_plan(client, project):
    # Research phase
    print_colored("Conducting market research...", Fore.CYAN)
    simulate_progress(1)
    research_response = client.run(research_agent, [{"role": "user", "content": project.key_info}])
    project.research_data = research_response.messages[-1]['content']

    # Creative phase
    print_colored("Developing ad concept...", Fore.CYAN)
    simulate_progress(1)
    creative_response = client.run(creative_agent, [{"role": "user", "content": f"Create ad concept based on this research: {project.research_data}"}])
    project.ad_concept = creative_response.messages[-1]['content']

    # Media phase
    print_colored("Creating media plan...", Fore.CYAN)
    simulate_progress(1)
    media_response = client.run(media_agent, [{"role": "user", "content": f"Create a media plan based on this concept: {project.ad_concept}"}])
    project.media_plan = media_response.messages[-1]['content']

    # Social Media phase
    print_colored("Developing social media strategy...", Fore.CYAN)
    simulate_progress(1)
    social_response = client.run(social_media_agent, [{"role": "user", "content": f"Create a social media strategy based on this concept and media plan: {project.ad_concept}, {project.media_plan}"}])
    project.social_strategy = social_response.messages[-1]['content']

    # SEO phase
    print_colored("Creating SEO plan...", Fore.CYAN)
    simulate_progress(1)
    seo_response = client.run(seo_agent, [{"role": "user", "content": f"Develop an SEO strategy based on: {project.research_data}, {project.ad_concept}"}])
    project.seo_plan = seo_response.messages[-1]['content']

    # Analytics phase
    print_colored("Setting up analytics plan...", Fore.CYAN)
    simulate_progress(1)
    analytics_response = client.run(analytics_agent, [{"role": "user", "content": f"Create an analytics plan for the campaign based on: {project.media_plan}, {project.social_strategy}, {project.seo_plan}"}])
    project.analytics_plan = analytics_response.messages[-1]['content']

    # Final summary
    print_colored("Generating final summary...", Fore.CYAN)
    simulate_progress(1)
    summary_prompt = f"""Summarize the complete marketing plan based on all collected data:
    Research: {project.research_data}
    Ad Concept: {project.ad_concept}
    Media Plan: {project.media_plan}
    Social Media Strategy: {project.social_strategy}
    SEO Plan: {project.seo_plan}
    Analytics Plan: {project.analytics_plan}
    """
    final_summary = client.run(summarization_agent, [{"role": "user", "content": summary_prompt}])

    return final_summary.messages[-1]['content']

def improved_workflow(client, initial_query):
    project = ImprovedProject()

    # Step 1: Query Understanding
    print_colored("Analyzing your query...", Fore.CYAN)
    simulate_progress(1)  # Simulate 1 second of processing
    nlp_response = client.run(nlp_agent, [{"role": "user", "content": initial_query}])
    project.query_type, project.key_info = parse_nlp_response(nlp_response)

    # Step 2: User Confirmation
    confirmation = get_user_confirmation(project.query_type, project.key_info)
    if not confirmation:
        return "I apologize for the misunderstanding. Could you please rephrase your query?"

    # Step 3: Dynamic Workflow
    print_colored("Processing your request...", Fore.CYAN)
    if project.query_type == "information_request":
        simulate_progress(2)  # Simulate 2 seconds of processing
        response = handle_information_request(client, project)
    elif project.query_type == "marketing_plan":
        simulate_progress(5)  # Simulate 5 seconds of processing
        response = handle_marketing_plan(client, project)
    else:
        return "I'm sorry, I couldn't determine how to handle your request. Could you please try rephrasing it?"

    return response

def get_user_feedback():
    while True:
        feedback = input(Fore.YELLOW + "Was this response helpful? (yes/no): " + Style.RESET_ALL).lower()
        if feedback == 'yes':
            return True
        elif feedback == 'no':
            return False
        print_colored("Please answer with 'yes' or 'no'.", Fore.RED)

# Set up your Swarm client
client = Swarm()

# Main execution
if __name__ == "__main__":
    print_colored("Welcome to our World Class Ad Agency. How can we assist you today?", Fore.GREEN)

    while True:
        initial_query = input(Fore.CYAN + "Please enter your query (or type 'exit' to quit): " + Style.RESET_ALL)
        chat_history.add("user", initial_query)

        if initial_query.lower() == 'exit':
            print_colored("Thank you for using our service. Goodbye!", Fore.GREEN)
            break

        try:
            response = improved_workflow(client, initial_query)
            print_colored("\nHere's our response:\n", Fore.GREEN)
            print(response)
            chat_history.add("assistant", response)

            if get_user_feedback():
                print_colored("Great! I'm glad the response was helpful.", Fore.GREEN)
            else:
                print_colored("I apologize that the response wasn't helpful. Let me try to improve.", Fore.YELLOW)
                continue

            follow_up = input(Fore.YELLOW + "Do you need any more information? (yes/no): " + Style.RESET_ALL).lower()
            if follow_up == 'no':
                print_colored("Thank you for using our service. If you have any more questions, feel free to ask!", Fore.GREEN)
            # If 'yes', the loop continues and asks for a new query

        except Exception as e:
            print_colored(f"An error occurred: {str(e)}", Fore.RED)
            print_colored("I apologize for the inconvenience. Please try again or rephrase your query.", Fore.YELLOW)