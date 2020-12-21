CREATE TABLE users
(
    id          SERIAL NOT NULL,
    username    VARCHAR,
    name        VARCHAR,
    surname     VARCHAR,
    email       VARCHAR,
    password    VARCHAR,
    is_moderator BOOLEAN,
    PRIMARY KEY (id)
);


CREATE TABLE articles
(
    id          SERIAL  NOT NULL,
    title       VARCHAR NOT NULL,
    text        VARCHAR NOT NULL,
    author_id   INTEGER NOT NULL,

    FOREIGN KEY (author_id)
        REFERENCES users (id)
        ON DELETE CASCADE,
    PRIMARY KEY (id)
);

CREATE TABLE article_changes
(
    id          SERIAL  NOT NULL,
    title       VARCHAR NOT NULL,
    text        VARCHAR NOT NULL,
    article_id   INTEGER NOT NULL,
    author_id   INTEGER,

    FOREIGN KEY (article_id)
        REFERENCES articles (id)
        ON DELETE CASCADE,

    FOREIGN KEY (author_id)
        REFERENCES users (id)
        ON DELETE CASCADE,

    PRIMARY KEY (id)
);

-- CREATE TABLE author_article
-- (
--     author_id       INTEGER NOT NULL,
--     article_id      INTEGER NOT NULL,
--     PRIMARY KEY (author_id, article_id)
--     FOREIGN KEY (author_id) REFERENCES users (id),
--     FOREIGN KEY (article_id) REFERENCES articles (id)
-- );

-- CREATE TABLE list_of_article_changes
-- (
--     article_id          INTEGER NOT NULL,
--     articlechanges_id   INTEGER NOT NULL,
--
--     PRIMARY KEY (article_id, articlechanges_id)
--     FOREIGN KEY (article_id) REFERENCES articles (id),
--     FOREIGN KEY (articlechanges_id) REFERENCES articlechanges (id)
-- );
