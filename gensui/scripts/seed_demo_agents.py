"""Seed Gensui DB with demo agents for presentation purposes."""

import json
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone

DB_PATH = "gensui/data/gensui.db"

# Generate deterministic UUIDs for cross-referencing nexus peers
AGENT_IDS = {
    "alpha":    str(uuid.uuid5(uuid.NAMESPACE_DNS, "shogun-alpha")),
    "bravo":    str(uuid.uuid5(uuid.NAMESPACE_DNS, "shogun-bravo")),
    "charlie":  str(uuid.uuid5(uuid.NAMESPACE_DNS, "shogun-charlie")),
    "delta":    str(uuid.uuid5(uuid.NAMESPACE_DNS, "shogun-delta")),
    "echo":     str(uuid.uuid5(uuid.NAMESPACE_DNS, "shogun-echo")),
    "foxtrot":  str(uuid.uuid5(uuid.NAMESPACE_DNS, "shogun-foxtrot")),
    "ghost":    str(uuid.uuid5(uuid.NAMESPACE_DNS, "shogun-ghost")),
}

now = datetime.now(timezone.utc)

DEMO_AGENTS = [
    {
        "id": AGENT_IDS["alpha"],
        "instance_name": "Shogun Alpha",
        "hostname": "srv-alpha.prod.local",
        "environment": "production",
        "organization": "AlphaHorizon AI",
        "owner": "admin@alphahorizon.ai",
        "version": "1.4.4",
        "enrollment_status": "active",
        "status": "online",
        "last_seen_at": (now - timedelta(seconds=12)).isoformat(),
        "harakiri_state": "none",
        "local_os": "Ubuntu 24.04 LTS",
        "deployment_type": "docker",
        "samurai_count": 5,
        "active_workflow_count": 2,
        "active_mado_sessions": 1,
        "metadata_json": json.dumps({
            "nexus_peers": [AGENT_IDS["bravo"], AGENT_IDS["charlie"]],
        }),
    },
    {
        "id": AGENT_IDS["bravo"],
        "instance_name": "Shogun Bravo",
        "hostname": "srv-bravo.prod.local",
        "environment": "production",
        "organization": "AlphaHorizon AI",
        "owner": "admin@alphahorizon.ai",
        "version": "1.4.4",
        "enrollment_status": "active",
        "status": "online",
        "last_seen_at": (now - timedelta(seconds=8)).isoformat(),
        "harakiri_state": "none",
        "local_os": "Ubuntu 24.04 LTS",
        "deployment_type": "docker",
        "samurai_count": 3,
        "active_workflow_count": 1,
        "active_mado_sessions": 0,
        "metadata_json": json.dumps({
            "nexus_peers": [AGENT_IDS["alpha"], AGENT_IDS["charlie"]],
        }),
    },
    {
        "id": AGENT_IDS["charlie"],
        "instance_name": "Shogun Charlie",
        "hostname": "srv-charlie.staging.local",
        "environment": "staging",
        "organization": "AlphaHorizon AI",
        "owner": "dev-team@alphahorizon.ai",
        "version": "1.4.3",
        "enrollment_status": "active",
        "status": "online",
        "last_seen_at": (now - timedelta(seconds=20)).isoformat(),
        "harakiri_state": "none",
        "local_os": "Debian 12",
        "deployment_type": "bare-metal",
        "samurai_count": 8,
        "active_workflow_count": 4,
        "active_mado_sessions": 2,
        "metadata_json": json.dumps({
            "nexus_peers": [AGENT_IDS["alpha"], AGENT_IDS["bravo"]],
        }),
    },
    {
        "id": AGENT_IDS["delta"],
        "instance_name": "Shogun Delta",
        "hostname": "edge-delta.eu-west.local",
        "environment": "production",
        "organization": "AlphaHorizon AI",
        "owner": "ops@alphahorizon.ai",
        "version": "1.4.4",
        "enrollment_status": "active",
        "status": "online",
        "last_seen_at": (now - timedelta(seconds=5)).isoformat(),
        "harakiri_state": "none",
        "local_os": "Windows Server 2025",
        "deployment_type": "vm",
        "samurai_count": 2,
        "active_workflow_count": 1,
        "active_mado_sessions": 0,
        "metadata_json": json.dumps({
            "nexus_peers": [AGENT_IDS["echo"], AGENT_IDS["alpha"]],
        }),
    },
    {
        "id": AGENT_IDS["echo"],
        "instance_name": "Shogun Echo",
        "hostname": "edge-echo.eu-west.local",
        "environment": "production",
        "organization": "AlphaHorizon AI",
        "owner": "ops@alphahorizon.ai",
        "version": "1.4.2",
        "enrollment_status": "active",
        "status": "offline",
        "last_seen_at": (now - timedelta(hours=3)).isoformat(),
        "harakiri_state": "none",
        "local_os": "Ubuntu 22.04 LTS",
        "deployment_type": "docker",
        "samurai_count": 0,
        "active_workflow_count": 0,
        "active_mado_sessions": 0,
        "metadata_json": json.dumps({
            "nexus_peers": [AGENT_IDS["delta"], AGENT_IDS["foxtrot"]],
        }),
    },
    {
        "id": AGENT_IDS["foxtrot"],
        "instance_name": "Shogun Foxtrot",
        "hostname": "lab-foxtrot.dev.local",
        "environment": "development",
        "organization": "AlphaHorizon AI",
        "owner": "researcher@alphahorizon.ai",
        "version": "1.4.4",
        "enrollment_status": "active",
        "status": "online",
        "last_seen_at": (now - timedelta(seconds=45)).isoformat(),
        "harakiri_state": "none",
        "local_os": "macOS 15.4 Sequoia",
        "deployment_type": "native",
        "samurai_count": 12,
        "active_workflow_count": 6,
        "active_mado_sessions": 3,
        "metadata_json": json.dumps({
            "nexus_peers": [AGENT_IDS["echo"], AGENT_IDS["charlie"]],
        }),
    },
    {
        "id": AGENT_IDS["ghost"],
        "instance_name": "Shogun Ghost",
        "hostname": "compromised-node.internal",
        "environment": "unknown",
        "organization": "AlphaHorizon AI",
        "owner": "admin@alphahorizon.ai",
        "version": "1.3.0",
        "enrollment_status": "active",
        "status": "online",
        "last_seen_at": (now - timedelta(minutes=10)).isoformat(),
        "harakiri_state": "soft_freeze",
        "local_os": "Linux (unknown)",
        "deployment_type": "unknown",
        "samurai_count": 1,
        "active_workflow_count": 0,
        "active_mado_sessions": 0,
        "metadata_json": json.dumps({
            "nexus_peers": [],
        }),
    },
]

# Columns to insert
COLUMNS = [
    "id", "instance_name", "hostname", "environment", "organization", "owner",
    "version", "enrollment_status", "status", "last_seen_at", "harakiri_state",
    "local_os", "deployment_type", "samurai_count", "active_workflow_count",
    "active_mado_sessions", "metadata_json", "disconnect_behavior", "created_at",
    "updated_at",
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Clean up any previous demo agents
    demo_ids = tuple(AGENT_IDS.values())
    placeholders = ",".join("?" * len(demo_ids))
    cur.execute(f"DELETE FROM shogun_members WHERE id IN ({placeholders})", demo_ids)

    for agent in DEMO_AGENTS:
        values = [
            agent["id"],
            agent["instance_name"],
            agent["hostname"],
            agent["environment"],
            agent["organization"],
            agent["owner"],
            agent["version"],
            agent["enrollment_status"],
            agent["status"],
            agent["last_seen_at"],
            agent["harakiri_state"],
            agent["local_os"],
            agent["deployment_type"],
            agent["samurai_count"],
            agent["active_workflow_count"],
            agent["active_mado_sessions"],
            agent["metadata_json"],
            "CONTINUE_LAST_POLICY",
            now.isoformat(),
            now.isoformat(),
        ]
        placeholders_row = ",".join("?" * len(COLUMNS))
        cols = ",".join(COLUMNS)
        cur.execute(f"INSERT INTO shogun_members ({cols}) VALUES ({placeholders_row})", values)
        print(f"  + {agent['instance_name']} ({agent['status']}) - {agent['environment']}")

    conn.commit()
    conn.close()
    print(f"\nDone! Seeded {len(DEMO_AGENTS)} demo agents into {DB_PATH}")


if __name__ == "__main__":
    seed()
