begin;

DROP TABLE IF EXISTS Pitch;
DROP TABLE IF EXISTS Runner;
DROP TABLE IF EXISTS Atbat;
DROP TABLE IF EXISTS Playeringame;
DROP TABLE IF EXISTS Game;
DROP TABLE IF EXISTS Stadium;
DROP TABLE IF EXISTS Player;
DROP TABLE IF EXISTS Team;
DROP TABLE IF EXISTS gamedir;

CREATE TABLE stadium (
   id INTEGER PRIMARY KEY,
   name VARCHAR(128),
   location VARCHAR(128)
);

CREATE TABLE team (
   id INTEGER,
code CHAR(3) PRIMARY KEY,
name VARCHAR(64),
name_full VARCHAR(128),
name_brief VARCHAR(64)
);

CREATE TABLE player (
   id INTEGER PRIMARY KEY,
   first VARCHAR(64),
   last VARCHAR(64),
   boxname VARCHAR(64),
   rl CHAR(1) -- does this change?
);

CREATE TABLE game (
   game_pk INTEGER PRIMARY KEY,
   type CHAR(1),

   away_team_code CHAR(3),
   home_team_code CHAR(3),
   away_fname VARCHAR(42),
   home_fname VARCHAR(42),
   away_sname VARCHAR(16),
   home_sname VARCHAR(16),
   stadium INTEGER,
   date VARCHAR(32),

   FOREIGN KEY (away_team_code) REFERENCES team (code),
   FOREIGN KEY (home_team_code) REFERENCES team (code)
);

CREATE TABLE playeringame (
   id INTEGER NOT NULL,
   num INTEGER, -- this changes
   position CHAR(2),
   bat_order INTEGER,
   game_position CHAR(2), -- the difference?
   avg FLOAT,
   hr INTEGER,
   rbi INTEGER,
   wins INTEGER,
   losses INTEGER,
   era FLOAT,

   game_pk INTEGER NOT NULL,

   FOREIGN KEY (id) REFERENCES player (id),
   FOREIGN KEY (game_pk) REFERENCES game (game_pk),
   PRIMARY KEY (id, game_pk)
);

CREATE TABLE atbat (

   inning INTEGER,
   num INTEGER NOT NULL,
   b INTEGER,
   s INTEGER,
   batter INTEGER,
   stand CHAR(1),
   p_throws CHAR(1),
   b_height  VARCHAR(32),
   pitcher INTEGER,
   des  VARCHAR(512),
   event  VARCHAR(128),
   brief_event  VARCHAR(128),

   game_pk INTEGER NOT NULL,
   date VARCHAR(32),
   
   FOREIGN KEY (game_pk) REFERENCES game (game_pk),
   FOREIGN KEY (batter) REFERENCES player (id),
   FOREIGN KEY (pitcher) REFERENCES player (id),
   PRIMARY KEY (game_pk, num)

);

{% if postgres %}
CREATE SEQUENCE runner_runner_pk_seq  --:POSTGRES
    INCREMENT BY 1 --:POSTGRES
    NO MAXVALUE --:POSTGRES
    NO MINVALUE --:POSTGRES
    CACHE 1; --:POSTGRES
{% endif %}


CREATE TABLE runner (
{% if postgres %}
   runner_pk INTEGER DEFAULT nextval('runner_runner_pk_seq') PRIMARY KEY, --POSTGRES
{% else %}
   runner_pk INTEGER PRIMARY KEY, --SQLITE
{% endif %}

   atbatnum INTEGER,
   game_pk INTEGER,

   id INTEGER,
   "start" VARCHAR(4),
   "end" VARCHAR(4),
   score CHAR(1),
   rbi CHAR(1),
   earned CHAR(1),
   event VARCHAR(128),

   FOREIGN KEY (atbatnum, game_pk) REFERENCES atbat (num, game_pk),
   FOREIGN KEY (game_pk) REFERENCES game (game_pk),
   FOREIGN KEY (id) REFERENCES player (id)
);

CREATE TABLE pitch (
   des VARCHAR(256),
   type CHAR(1),
   id INTEGER,
   x FLOAT,
   y FLOAT,
   sv_id VARCHAR(128),
   start_speed float,
   end_speed FLOAT,
   sz_top FLOAT,
   sz_bot FLOAT,
   pfx_x FLOAT,
   pfx_z FLOAT,
   px FLOAT,
   pz FLOAT,
   x0 FLOAT,
   y0 FLOAT,
   z0 FLOAT,
   vx0 FLOAT,
   vy0 FLOAT,
   vz0 FLOAT,
   ax FLOAT,
   ay FLOAT,
   az FLOAT,
   break_y FLOAT,
   break_angle FLOAT,
   break_length FLOAT,
   pitch_type VARCHAR(4),
   type_confidence FLOAT,
   spin_dir FLOAT,
   spin_rate FLOAT,
   nasty INTEGER,
   on_1b INTEGER,
   on_2b INTEGER,
   on_3b INTEGER,
   {% if postgres %}
   payoff BOOLEAN, --POSTGRES
   {% else %}
   payoff INTEGER, --SQLITE
   {% endif %}
   balls INTEGER,
   strikes INTEGER,

   game_pk INTEGER,
   pitcher INTEGER,
   batter INTEGER,
   atbatnum INTEGER,
   FOREIGN KEY (pitcher) REFERENCES player (id),
   FOREIGN KEY (batter) REFERENCES player (id),
   FOREIGN KEY (on_1b) REFERENCES player (id),
   FOREIGN KEY (on_2b) REFERENCES player (id),
   FOREIGN KEY (on_3b) REFERENCES player (id),
   FOREIGN KEY (game_pk, atbatnum) REFERENCES atbat (game_pk, num),

   PRIMARY KEY (game_pk, id)
);

CREATE INDEX atbat_game on atbat (game_pk);
CREATE INDEX atbat_batter on atbat (batter);
CREATE INDEX atbat_pitcher on atbat (pitcher);
CREATE INDEX playeringame_player on playeringame (id);
CREATE INDEX playeringame_game on playeringame (game_pk);
CREATE INDEX game_away on game (away_team_code);
CREATE INDEX game_home on game (home_team_code);
CREATE INDEX pitch_pitcher on pitch (pitcher);
CREATE INDEX pitch_batter on pitch (batter);
CREATE INDEX pitch_atbat on pitch (game_pk, atbatnum);




-- administration tables_file
CREATE TABLE gamedir (
    gamedir_id INTEGER,
    local_copy BOOLEAN NOT NULL DEFAULT FALSE,
    url TEXT,
    path TEXT,
    status TEXT NOT NULL,      -- or enum? final, postponed, error, what else?
    status_long TEXT,      -- exactly what's the problem officer
    loaded BOOLEAN NOT NULL DEFAULT FALSE,
    game_pk INTEGER,

    FOREIGN KEY (game_pk) REFERENCES game(game_pk),
    PRIMARY KEY (gamedir_id)
);
{% if postgres %}
create or replace language plpgsql;

--create or replace aggregate avg(float)
--(
--sfunc = accu
--);

--create or replace aggregate normalize(float)
--(
--    sfunc=array_ap

-- want to normalize...
-- start_speed
-- pfx_x (flip for sinisters)
-- pfx_z
-- release point?

CREATE OR REPLACE FUNCTION normalized_speed(get_game_pk INTEGER, get_num INTEGER) RETURNS FLOAT AS
$normalized_speed$
-- takes the primary key of a pitch.
-- returns that pitch's speed normalized to the range [0,1.0]
-- where 0 is the slowest and 1.0 the fastest pitch
-- thrown by that pitcher

-- using the very slowest pitch is bad because over the course of a season,
-- that's probably an intentional ball: very slow indeed.
-- What's the slowest "in anger" pitch?
-- want to take 10th percentile probably

declare
    start_speed_to_normalize float;
    pitcher_pk INTEGER;
    fastest float;
    slowest float;
begin
    
        select start_speed, pitcher from pitch where game_pk=get_game_pk
        and id = get_num into start_speed_to_normalize, pitcher_pk;
        select avg(start_speed) + 2 * stddev(start_speed) from pitch where pitcher = pitcher_pk
            into fastest;
        select avg(start_speed) - 2*stddev(start_speed) from pitch where pitcher = pitcher_pk
            into slowest;
        return 2* (start_speed_to_normalize - slowest) / (fastest - slowest) - 0.5 ;
end;
$normalized_speed$ language 'plpgsql';

CREATE OR REPLACE FUNCTION lefty(p_throws char) 
RETURNS INTEGER AS
$lefty$
BEGIN
    IF p_throws = 'L' THEN
        RETURN 1;
    ELSE
        RETURN -1;
    END IF;
END;
$lefty$ LANGUAGE 'plpgsql';

{% endif %}

{% if ranges %}
--CREATE TABLE ranges (
--    low_speed FLOAT,
--    high_speed FLOAT,
--    low_pfx_x FLOAT,
--    high_pfx_x FLOAT,
--    low_pfx_x FLOAT,
--    high_pfx_x FLOAT,
--    pitcher_id INTEGER,
--
--    PRIMARY KEY (pitcher_id),
--    FOREIGN KEY (pitcher_id) REFERENCES player (id)
--);
--




--    FOREIGN KEY (pitcher) references player (id),
--    primary key (pitcher)
CREATE VIEW RANGES AS 
    SELECT pitch.pitcher, 
    avg(start_speed) - 2*stddev(start_speed) as low_speed,
    avg(start_speed) + 2 * stddev(start_speed) as high_speed,
    (avg(pfx_x * lefty(p_throws)) - 2*stddev(pfx_x * lefty(p_throws))) as low_pfx_x,
    (avg(pfx_x * lefty(p_throws)) + 2*stddev(pfx_x * lefty(p_throws))) as high_pfx_x,
    avg(pfx_z) - 2*stddev(pfx_z) as low_pfx_z,
    avg(pfx_z) + 2*stddev(pfx_z) as high_pfx_z
    FROM pitch 
    join atbat on pitch.atbatnum = atbat.num and pitch.game_pk = atbat.game_pk
    GROUP BY pitch.pitcher;

{% endif %}



commit;
