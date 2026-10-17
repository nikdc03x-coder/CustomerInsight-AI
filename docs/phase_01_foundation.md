# Phase 01 — Research Foundation

## Project

CustomerInsight AI

## Research title

CustomerInsight AI: An Explainable Machine Learning
Framework for Customer Behaviour Discovery and
Segmentation Analysis

## 1. Background

Retail businesses generate transaction data through
everyday purchases. These records can reveal useful
patterns about customer spending and purchasing habits.

However, raw transaction data does not directly explain
why customers behave differently or how consistently
machine learning models can identify these differences.

This project investigates whether unsupervised learning
can discover meaningful customer groups and how
reliably those groups can be interpreted.

## 2. Research problem

Clustering algorithms can divide customers into groups,
but different algorithms may produce different results.

We want to understand how the choice of algorithm,
data preparation and noise affects the reliability
and interpretability of customer segmentation.

## 3. Research questions

RQ1: How do different clustering algorithms compare
when segmenting customers using purchasing behaviour?

RQ2: How stable are the discovered customer segments
when the dataset is resampled or contains noise?

RQ3: How can the identified customer groups be
explained using understandable behavioural features?

## 4. Initial hypotheses

H1: Clustering algorithms will produce differences
in segmentation quality on the same dataset.

H2: Adding noise or changing the dataset sample may
affect the stability of the discovered clusters.

H3: Purchasing features such as recency, frequency
and monetary value can help describe the segments.

These are hypotheses to investigate, not findings.

## 5. Research methodology

We plan to:

1. Select a public retail transaction dataset.
2. Examine its quality and document preprocessing.
3. Create customer-level behavioural features.
4. Compare multiple clustering algorithms.
5. Measure clustering quality and stability.
6. Investigate how to interpret customer segments.
7. Present the findings using understandable charts.

## 6. Technology choices

Python:
Main programming language.

Pandas:
Loading, checking and transforming tabular data.

scikit-learn:
Clustering algorithms and evaluation metrics.

Plotly:
Interactive charts for exploring customer behaviour.

Streamlit:
An application for presenting research findings.

pytest:
Testing the reusable software components.

## 7. Phase 01 implementation

The initial software foundation includes:

- A structured Python project.
- A reusable transaction-loading module.
- Basic dataset validation.
- A demonstration dataset.
- Automated tests.

The demonstration dataset is synthetic and is used
only to test the pipeline.

## 8. Experimental status

No clustering experiments have been conducted yet.

No claims about algorithm performance, model
stability or customer behaviour are made in this phase.

## 9. Limitations

The transaction schema is preliminary and may change
after examining the selected research dataset.

The current validation does not cover all possible
data quality issues.

The current tests verify only foundational operations.

## 10. Next phase

Select a suitable public research dataset and perform
systematic exploratory data analysis.

We will document missing values, duplicates,
returns, unusual transactions and preprocessing choices.

## 11. Phase completion record

Status: Not yet verified

Dataset source: To be selected

Test results: To be recorded after execution

Git commit: To be recorded after successful testing
