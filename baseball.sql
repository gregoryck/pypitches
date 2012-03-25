begin;

--drop table pitch;
--drop table runner;
--drop table atbat;
--drop table playeringame;
--drop table game;
--drop table stadium;
--drop table player;
--drop table team;

create function normalized_speed(integer) returns float as
$normalized_speed$
declare
    id alias for $1;
begin

end;
$normalized_speed$ language pgsql;

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

CREATE SEQUENCE runner_runner_pk_seq  --:POSTGRES
    INCREMENT BY 1 --:POSTGRES
    NO MAXVALUE --:POSTGRES
    NO MINVALUE --:POSTGRES
    CACHE 1; --:POSTGRES


CREATE TABLE runner (
   runner_pk INTEGER DEFAULT nextval('runner_runner_pk_seq') PRIMARY KEY, --:POSTGRES

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
   payoff BOOLEAN, --:POSTGRES
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

commit;
