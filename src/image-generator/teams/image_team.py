from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import SelectorGroupChat, RoundRobinGroupChat
from aagents.image_agents import get_prompt_engineer_agent, get_critic_agent, get_generator_agent
from core.model import get_model_client

def get_image_team():
    # Define agents
    prompt_agent = get_prompt_engineer_agent()
    critic_agent = get_critic_agent()
    generator_agent = get_generator_agent()
    
    # Termination: Stop when image is generated or max messages reached
    text_termination = TextMentionTermination("Image generated successfully")
    max_message_termination = MaxMessageTermination(15)
    termination = text_termination | max_message_termination

    # We use a linear Round Robin for simplicity in this specific flow 
    # as it's predictable: Prompt -> Critic -> Generator (which skips if not ready) 
    # But Selector is better for the loop of Prompt <-> Critic.
    
    # Let's try RoundRobin first but we need to ensure Generator speaks only when ready.
    # Actually, Selector is safer if we give it good instructions.
    
    image_team = RoundRobinGroupChat(
        [prompt_agent, critic_agent, generator_agent],
        termination_condition=termination
    )
    
    return image_team
