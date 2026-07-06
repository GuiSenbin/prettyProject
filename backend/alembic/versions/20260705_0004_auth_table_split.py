"""auth table split

Revision ID: 20260705_0004
Revises: 20260705_0003
Create Date: 2026-07-05 14:52:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260705_0004'
down_revision = '20260705_0003'
branch_labels = None
depends_on = None


def upgrade():
    # 1. 预先删除被 SQLAlchemy 自动建立的同名空表，防止创建冲突
    op.execute("DROP TABLE IF EXISTS user_social_auths")

    # 2. 创建新表 user_social_auths
    op.create_table(
        'user_social_auths',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('identity_type', sa.String(length=20), nullable=False),
        sa.Column('identifier', sa.String(length=100), nullable=False),
        sa.Column('credential', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('identity_type', 'identifier', name='uq_auth_type_identifier')
    )
    op.create_index(op.f('ix_user_social_auths_id'), 'user_social_auths', ['id'], unique=False)

    # 3. 第一阶段：先将 users.phone 更改为 nullable=True (允许为空)，暂不创建唯一约束以防冲突
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('phone', existing_type=sa.String(length=32), nullable=True)

    # 4. 第二阶段：由于现在 phone 列已经允许 NULL 写入，我们执行 SQL 数据清洗
    # 把空字符串和重复的 phone 字段全部更新为 NULL
    op.execute("UPDATE users SET phone = NULL WHERE phone = ''")
    op.execute(
        "UPDATE users SET phone = NULL WHERE id NOT IN ("
        "  SELECT MIN(id) FROM users WHERE phone IS NOT NULL GROUP BY phone"
        ")"
    )

    # 5. 第三阶段：将清洗后有效的真实 phone 迁移至 user_social_auths 中
    op.execute(
        "INSERT INTO user_social_auths (user_id, identity_type, identifier, created_at, updated_at) "
        "SELECT id, 'phone', phone, created_at, updated_at FROM users WHERE phone IS NOT NULL"
    )

    # 6. 第四阶段：清洗完结后，现在数据已不存在重复手机号，我们可以安全地在 users 上建立唯一性约束
    with op.batch_alter_table('users') as batch_op:
        batch_op.create_unique_constraint('uq_users_phone', ['phone'])


def downgrade():
    op.drop_index(op.f('ix_user_social_auths_id'), table_name='user_social_auths')
    op.drop_table('user_social_auths')
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('uq_users_phone', type_='unique')
        batch_op.alter_column('phone', existing_type=sa.String(length=32), nullable=False)
