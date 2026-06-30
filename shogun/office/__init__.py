"""Katana Office Adapter — Controlled Microsoft Office automation for Shogun.

This package provides governed, permission-bound, auditable access to
Microsoft Office applications (Excel, Word, PowerPoint, Outlook) through
structured tool calls rather than raw desktop control.

Architecture:
    Shogun Agent
      → Tool Permission Engine
        → Office Adapter Layer (this package)
          → Application Adapters (Excel, Word, PPT, Outlook)
            → openpyxl / python-docx / python-pptx / pywin32 COM

Key design principles:
  - Agents never talk directly to COM automation
  - Every file path is validated against approved folder boundaries
  - Every action is checked against the current security posture
  - Every operation is logged through the EventLogger dual-write pipeline
  - COM calls run on a dedicated STA thread pool
  - One global mutex per Office application prevents concurrency issues
"""
