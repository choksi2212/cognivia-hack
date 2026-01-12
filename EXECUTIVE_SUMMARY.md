# SITARA - Executive Summary

## Situational Risk Intelligence Platform for Women's Safety in India

**The Problem:** Women's safety solutions today are reactive, fragmented, and poorly contextualized for Indian environments. Existing panic buttons trigger alerts only after danger occurs, ignore gradual risk accumulation, and fail to account for India's unique urban infrastructure—narrow lanes, mixed land-use zones, and poorly lit localities.

**Our Solution:** SITARA is an agentic AI safety platform that provides **preventive risk awareness**, not reactive panic responses. It continuously evaluates environmental and temporal risk using real OpenStreetMap data and Indian crime statistics, employing a Random Forest ML model (94-96% accuracy) to predict risk levels. An intelligent agent layer decides when and how to intervene proportionally—suggesting safer routes, enabling silent check-ins, or recommending escalation based on risk velocity.

**Why Agentic AI?** Unlike traditional ML systems that merely output scores, SITARA observes continuously, maintains state over time, reasons about intervention necessity, and acts with user-controlled, proportional responses.

**Technical Stack:** Next.js 14 frontend, FastAPI backend, PostgreSQL database, scikit-learn ML models, real-time OSM feature extraction, comprehensive edge case testing, and full data persistence.

**Impact:** Even a 5-10% reduction in high-risk exposure saves lives at population scale while empowering better decisions through situational intelligence.
