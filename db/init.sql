CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- THREADS
-- =====================================================

CREATE TABLE threads (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- =====================================================
-- RAW MESSAGES
-- =====================================================

CREATE TABLE raw_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    thread_id TEXT NOT NULL,
    source_message_id TEXT UNIQUE
    parent_message_id UUID,
    author TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    content TEXT NOT NULL,
    channel TEXT,

    CONSTRAINT fk_raw_messages_thread
        FOREIGN KEY (thread_id)
        REFERENCES threads(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_raw_messages_parent
        FOREIGN KEY (parent_message_id)
        REFERENCES raw_messages(id)
        ON DELETE SET NULL
);

-- =====================================================
-- MESSAGE CLASSIFICATION
-- =====================================================

CREATE TABLE classified_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    raw_message_id UUID NOT NULL,

    role TEXT NOT NULL,
    confidence DOUBLE PRECISION,

    CONSTRAINT fk_classified_raw_message
        FOREIGN KEY (raw_message_id)
        REFERENCES raw_messages(id)
        ON DELETE CASCADE
);

-- =====================================================
-- KNOWLEDGE OBJECTS
-- =====================================================

CREATE TABLE knowledge_objects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    thread_id TEXT NOT NULL,

    problem TEXT,
    context TEXT,

    symptoms JSONB,
    solutions_tried JSONB,

    confirmed_solution TEXT,
    technology TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_knowledge_thread
        FOREIGN KEY (thread_id)
        REFERENCES threads(id)
        ON DELETE CASCADE
);

-- =====================================================
-- INDEXES
-- =====================================================

CREATE INDEX idx_raw_messages_thread_id
    ON raw_messages(thread_id);

CREATE INDEX idx_raw_messages_parent_message_id
    ON raw_messages(parent_message_id);

CREATE INDEX idx_raw_messages_timestamp
    ON raw_messages(timestamp);

CREATE INDEX idx_classified_messages_raw_message_id
    ON classified_messages(raw_message_id);

CREATE INDEX idx_knowledge_objects_thread_id
    ON knowledge_objects(thread_id);

CREATE INDEX idx_knowledge_objects_technology
    ON knowledge_objects(technology);

