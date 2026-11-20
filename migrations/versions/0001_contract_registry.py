"""Initial contract registry tables."""
from alembic import op
from app.persistence import Base

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Uses the same SQLAlchemy metadata as the ORM, avoiding duplicate definitions.
    Base.metadata.create_all(bind=op.get_bind())

def downgrade():
    Base.metadata.drop_all(bind=op.get_bind())
