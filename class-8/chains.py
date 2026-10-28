"""LangChain prompts and chains for shipment exception reports."""

import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


MODEL_NAME = "openai/gpt-oss-20b"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def create_chains():
    """Create the classifier and the two response-writing LangChain chains."""
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing from your .env file.")

    model = ChatOpenAI(
        model=MODEL_NAME,
        temperature=0,
        api_key=api_key,
        base_url=GROQ_BASE_URL,
    )
    parser = StrOutputParser()

    classify_prompt = ChatPromptTemplate.from_template(
        "Classify the shipment exception report as exactly one of these "
        "categories: delayed, damaged, lost, or unknown.\n"
        "Use unknown if the report does not clearly describe a delay, damage, "
        "or lost shipment.\n"
        "Reply with only the category word.\n\n"
        "Report: {report}"
    )
    classify_chain = classify_prompt | model | parser

    escalate_prompt = ChatPromptTemplate.from_template(
        "Write a concise internal note for a logistics manager about this "
        "shipment exception. Include the category, customer tier, compensation "
        "amount, and reason it needs review.\n\n"
        "Category: {category}\n"
        "Customer tier: {customer_tier}\n"
        "Compensation amount: ${compensation_amount}\n"
        "Exception report: {report}"
    )
    escalate_chain = escalate_prompt | model | parser

    email_prompt = ChatPromptTemplate.from_template(
        "Write a concise, professional email to the customer about their "
        "shipment exception. Explain the category and compensation amount "
        "clearly. Do not promise anything beyond the stated compensation.\n\n"
        "Category: {category}\n"
        "Customer tier: {customer_tier}\n"
        "Compensation amount: ${compensation_amount}\n"
        "Exception report: {report}"
    )
    draft_email_chain = email_prompt | model | parser

    return classify_chain, escalate_chain, draft_email_chain
