CREATE TABLE user (
    id INTEGER PRIMARY KEY NOT NULL,
    name1 VARCHAR(32) NOT NULL,
    surname1 VARCHAR(32) NOT NULL,
    sex VARCHAR(1) NOT NULL,
    birthdate DATETIME NOT NULL,
    location VARCHAR(256) NOT NULL,
    email VARCHAR(256) NOT NULL,
    password VARCHAR(128) NOT NULL,
    -- OPTIONAL FIELDS
    name2 VARCHAR(32),
    surname2 VARCHAR(32),
    genre VARCHAR(32),
    active BOOLEAN NOT NULL DEFAULT 1,
    photoUrl TEXT
);

CREATE TABLE doctor (
    id INTEGER PRIMARY KEY NOT NULL,
    FOREIGN KEY (id) REFERENCES user(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE administrative (
    id INTEGER PRIMARY KEY NOT NULL,
    FOREIGN KEY (id) REFERENCES user(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE patient (
    id INTEGER PRIMARY KEY NOT NULL,
    FOREIGN KEY (id) REFERENCES user(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE userPhone (
    id INTEGER NOT NULL,
    phone VARCHAR(32) NOT NULL,

    PRIMARY KEY(id,phone),
    FOREIGN KEY (id) REFERENCES user(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Nurses and Doctors might be specialized.
CREATE TABLE specialty (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(64) UNIQUE NOT NULL
);

CREATE TABLE DocHasSpec (
    idSpec INTEGER NOT NULL,
    idDoc INTEGER NOT NULL,

    PRIMARY KEY (idSpec,idDoc),
    FOREIGN KEY (idDoc) REFERENCES doctor(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idSpec) REFERENCES specialty(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE appointment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(128) NOT NULL,
    date date NOT NULL,
    -- OPTIONAL FIELDS
    startsAt DATETIME,
    endsAt DATETIME,
    etpp INTEGER,
    maxTurns INTEGER
); --etpp: estimated time per patient (tiempo estimado por turno de paciente en la consulta), en minutos

-- Branch significa sucursal, una cita medica tomara lugar en alguna de las sucursales.
CREATE TABLE branch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(64) UNIQUE NOT NULL,
    phoneNumber VARCHAR(64) NOT NULL,
    location VARCHAR(64) NOT NULL,
    googleMapsSrc TEXT
);

CREATE TABLE apTakesPlace (
    idAp INTEGER NOT NULL,
    idBranch INTEGER NOT NULL,

    PRIMARY KEY(idAp,idBranch),
    FOREIGN KEY(idAp) REFERENCES appointment(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(idBranch) REFERENCES Branch(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE assignedTo (
    idAp INTEGER NOT NULL,
    idDoc INTEGER NOT NULL,

    PRIMARY KEY(idAp),
    FOREIGN KEY (idDoc) REFERENCES doctor(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idAp) REFERENCES appointment(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE attendsTo (
    idAp INTEGER NOT NULL,
    idPa INTEGER NOT NULL,
    -- OPTIONAL FIELD
    motive VARCHAR(256),
    time DATETIME, --NULLABLE, but in case it's provided it should be unique with both idAp and idPa
    number INTEGER, --NULLABLE, but in case it's provided it should be unique with both idAp and idPa
    notes TEXT,
    
    UNIQUE (idAp, idPa),
    FOREIGN KEY (idAp) REFERENCES appointment(id),
    FOREIGN KEY (idPa) REFERENCES patient(id) 
);
-- time is calculated based on appointment.etpp, appointment.startsAt and appointment.endsAt 
-- number is calculated based on appointment.maxTurns and freeTurns.value (table containing the deleted records of attendTo that got an assigned turn).

CREATE TABLE clinicalSign (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(128) UNIQUE NOT NULL,
    -- OPTIONAL FIELD
    description VARCHAR(512)
);

CREATE TABLE disease (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(128) UNIQUE NOT NULL,
    -- OPTIONAL FIELD
    description VARCHAR(512)
);

CREATE TABLE symptom (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(128) UNIQUE NOT NULL,
    -- OPTIONAL FIELD
    description VARCHAR(512)
);

CREATE TABLE registersCs (
    idAp INTEGER NOT NULL,
    idPa INTEGER NOT NULL,
    idCs INTEGER NOT NULL,
    -- OPTIONAL FIELD
    detail VARCHAR(256),

    PRIMARY KEY(idAp,idPa,idCs),
    FOREIGN KEY (idAp, idPa) REFERENCES attendsTo(idAp, idPa)  ON UPDATE CASCADE,
    FOREIGN KEY (idCs) REFERENCES clinicalSign(id)  ON UPDATE CASCADE
);

CREATE TABLE registersSy (
    idAp INTEGER NOT NULL,
    idPa INTEGER NOT NULL,
    idSy INTEGER NOT NULL,
    -- OPTIONAL FIELD
    detail VARCHAR(256),
    
    PRIMARY KEY(idAp,idPa,idSy),
    FOREIGN KEY (idAp, idPa) REFERENCES attendsTo(idAp, idPa)  ON UPDATE CASCADE,
    FOREIGN KEY (idSy) REFERENCES symptom(id)  ON UPDATE CASCADE
);

CREATE TABLE diagnoses (
    idAp INTEGER NOT NULL,
    idPa INTEGER NOT NULL,
    idDis INTEGER NOT NULL,
    -- OPTIONAL FIELD
    detail VARCHAR(256),

    PRIMARY KEY(idAp,idPa,idDis),
    FOREIGN KEY (idAp, idPa) REFERENCES attendsTo(idAp, idPa) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idDis) REFERENCES disease(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- HELPERS

CREATE TABLE freeTurns(
    idAp INTEGER NOT NULL,
    value INTEGER NOT NULL,

    UNIQUE(idAp, value),
    FOREIGN KEY (idAp) REFERENCES appointment(id) ON DELETE CASCADE
); -- Keep track of the free turns of an appointment

CREATE TABLE freeTimes(
    idAp INTEGER NOT NULL,
    value TEXT NOT NULL,

    UNIQUE(idAp, value),
    FOREIGN KEY (idAp) REFERENCES appointment(id) ON DELETE CASCADE
); -- Keep track of the free times of an appointment

CREATE TRIGGER assignTurnAndTimeToAttendsTo 
    AFTER INSERT ON attendsTo
BEGIN
    UPDATE attendsTo SET number = (SELECT num FROM (SELECT MIN(value) OR (MAX(attendsTo.idAp) + 1 OR 1) AS num FROM freeTurns, attendsTo WHERE attendsTo.idAp = new.idAp AND freeTurns.idAp = new.idAp)) WHERE attendsTo.idAp = new.idAp;
	UPDATE attendsTo SET time = (SELECT value FROM freeTimes WHERE idAp = new.idAp LIMIT 1 OFFSET 0) WHERE attendsTo.idAp = new.idAp;
END; -- automatically assigned in case appointment.startsAt and appointment.endsAt were provided

CREATE trigger deleteFreeTurnAndTime
	AFTER UPDATE ON attendsTo
BEGIN
	DELETE FROM freeTurns WHERE freeTurns.value = new.number AND freeTurns.idAp = new.idAp;
	DELETE FROM freeTimes WHERE freeTimes.value = new.time AND freeTimes.idAp = new.idAp;
END; -- when a patient takes a turn and/or time, delete it/them from the freeTurns/freeTimes tables. 

CREATE TRIGGER addFreeTurnAndTime
    AFTER DELETE ON attendsTo WHEN old.number IS NOT NULL
BEGIN
    INSERT INTO freeTurns (idAp, value) VALUES (old.idAp, old.number);
	INSERT INTO freeTimes (idAp, value) VALUES (old.idAp, old.time);
END; -- when a patient cancels their scheduled appointment, add the number and time they took to the freeTurns/freeTimes tables.

-- If a number is already picked, or is not in range of (0, maxTurns) raise an error
-- If a time is already picked, or is not in range of (startsAt, endsAt) raise an error
-- If the appointment does not have maxTurns, but a number for a turn is trying to be inserted in attendsTo, raise an error 
-- If the appointment does not have startsAt and endsAt setted, but a time for a turn is trying to be inserted in attendsTo, raise an error
CREATE TRIGGER assignToAttendsTo 
    BEFORE INSERT ON attendsTo
BEGIN
    SELECT CASE WHEN ((SELECT COUNT(idAp) FROM attendsTo WHERE attendsTo.idAp = new.idAp) >= (SELECT maxTurns FROM appointment WHERE id = new.idAp))
        THEN RAISE(ABORT, 'max number of turns already reached')
    END;

    SELECT CASE WHEN new.number IS NOT NULL THEN
        CASE
            WHEN NOT EXISTS (SELECT 1 FROM appointment WHERE appointment.id = new.idAp AND appointment.maxTurns IS NOT NULL)
                THEN RAISE(ABORT, 'number of turns is not setted yet')

            WHEN EXISTS(SELECT 1 FROM attendsTo WHERE number = new.number AND idAp = new.idAp)
                THEN RAISE(ABORT, 'number is already picked')
            
            WHEN NOT EXISTS(SELECT 1 FROM appointment WHERE appointment.id = new.idAp AND (new.number > 0 and new.number <= appointment.maxTurns)) 
                THEN RAISE(ABORT, 'number is not in the range of 0 and maximum turns')
        END
    END;

    SELECT CASE WHEN new.time IS NOT NULL THEN
        CASE
            WHEN EXISTS (SELECT 1 FROM appointment WHERE appointment.id = new.idAp AND (appointment.startsAt IS NULL OR appointment.startsAt IS NULL))
                THEN RAISE(ABORT, 'start and end time for this appointment are not setted yet')

            WHEN EXISTS(SELECT 1 FROM attendsTo WHERE time = new.time AND idAp = new.idAp)
                THEN RAISE(ABORT, 'time is already picked')
            
            WHEN NOT EXISTS(SELECT 1 FROM appointment WHERE appointment.id = new.idAp AND (new.time >= appointment.startsAt AND new.time <= appointment.endsAt)) 
                THEN RAISE(ABORT, 'time is not in the range of start and end time for this appointment')
        END
    END;
END;