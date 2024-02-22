#!/bin/bash
if [ ! -d AnalysisVE ];
then
    python3 -m venv AnalysisVE
    AnalysisVE/bin/pip install -r requirements.txt
fi
AnalysisVE/bin/python AnalysisNoGenerate.py
