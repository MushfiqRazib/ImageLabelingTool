# test file for dbmanager

"""All tests for pytest-postgresql."""
import psycopg2
import pytest


QUERY = "CREATE TABLE test_Project_Details
(
  "Project_Id" integer NOT NULL DEFAULT nextval('"Project_Details_Project_Id_seq"'::regclass),
  "Project_Name" character varying NOT NULL,
  "In_LabelBox" boolean,
  CONSTRAINT "Project_Details_pkey" PRIMARY KEY ("Project_Id")
);"

@pytest.mark.parametrize('postgres', (
    'postgresql94',
    'postgresql95',
    'postgresql96',
    'postgresql10',
    pytest.param('postgresql111', marks=pytest.mark.xfail),
))
def test_postgresql_proc(request, postgres):
    """Test different postgresql versions."""
    postgresql_proc = request.getfixturevalue(postgres)
    assert postgresql_proc.running() is True

def test_main_postgres(postgresql):
    """Check main postgresql fixture."""
    cur = postgresql.cursor()
    cur.execute(QUERY)
    postgresql.commit()
    cur.close()
	
def test_two_postgreses(postgresql, postgresql2):
    """Check two postgresql fixtures on one test."""
    cur = postgresql.cursor()
    cur.execute(QUERY)
    postgresql.commit()
    cur.close()

    cur = postgresql2.cursor()
    cur.execute(QUERY)
    postgresql2.commit()
    cur.close()
	
	def test_project_table_exists(cursor):
    cursor.execute('select Project_Id from Project_Details')
    rs = cursor.fetchall()
    assert len(rs) == 0 
	
@pytest.mark.parametrize('_', range(2))
def test_postgres_terminate_connection(
        postgresql, _):
    """
    Test that connections are terminated between tests.
    And check that only one exists at a time.
    """
    cur = postgresql.cursor()
    cur.execute('SELECT * FROM Project_Details;')
    assert len(cur.fetchall()) == 1, 'there is always only one connection'
    cur.close()