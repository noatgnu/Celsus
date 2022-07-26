"""create all table

Revision ID: ed05eb39438c
Revises: 
Create Date: 2022-07-19 15:54:20.445080

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ed05eb39438c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('project',
                    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('project_id_seq'::regclass)"),
                              autoincrement=True, nullable=False),
                    sa.Column('title', sa.TEXT(), autoincrement=False, nullable=False),
                    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=False),
                    sa.Column('sampleProcessingProtocol', sa.TEXT(), autoincrement=False, nullable=False),
                    sa.Column('dataProcessingProtocol', sa.TEXT(), autoincrement=False, nullable=False),
                    sa.Column('experimentType', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
                    sa.Column('databaseVersion', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('password', sa.TEXT(), autoincrement=False, nullable=True),
                    sa.Column('enable', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('date_created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('date_updated', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', name='project_pkey'),
                    postgresql_ignore_search_path=False
                    )
    op.create_table('organism',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='organism_project_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='organism_pkey')
                    )
    op.create_table('user',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('username', sa.TEXT(), autoincrement=False, nullable=False),
                    sa.Column('password', sa.TEXT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('id', name='user_pkey'),
                    sa.UniqueConstraint('username', name='user_username_key')
                    )
    op.create_table('collaborator',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('contact', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='collaborator_project_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='collaborator_pkey')
                    )
    op.create_table('instrument',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='instrument_project_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='instrument_pkey')
                    )
    op.create_table('sampleAnnotation',
                    sa.Column('id', sa.INTEGER(),
                              server_default=sa.text('nextval(\'"sampleAnnotation_id_seq"\'::regclass)'),
                              autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
                    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='sampleAnnotation_project_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='sampleAnnotation_pkey')
                    )
    op.create_table('file',
                    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('file_id_seq'::regclass)"),
                              autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('fileType', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='file_project_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='file_pkey'),
                    postgresql_ignore_search_path=False
                    )
    op.create_table('comparison',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('fcColumn', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('significantColumn', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('file_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['file_id'], ['file.id'], name='comparison_file_id_fkey',
                                            ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='comparison_project_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='comparison_pkey')
                    )
    op.create_table('differentialAnalysisData',
                    sa.Column('id', sa.INTEGER(),
                              server_default=sa.text('nextval(\'"differentialAnalysisData_id_seq"\'::regclass)'),
                              autoincrement=True, nullable=False),
                    sa.Column('primary_id', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('gene_names', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('foldChange', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False,
                              nullable=True),
                    sa.Column('significant', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False,
                              nullable=True),
                    sa.Column('comparison_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['comparison_id'], ['comparison.id'],
                                            name='differentialAnalysisData_comparison_id_fkey', ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='differentialAnalysisData_pkey')
                    )
    op.create_table('cellType',
                    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"cellType_id_seq"\'::regclass)'),
                              autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='cellType_project_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='cellType_pkey')
                    )
    op.create_table('tissue',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='tissue_project_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='tissue_pkey')
                    )
    op.create_table('disease',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='disease_project_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='disease_pkey')
                    )
    op.create_table('sampleColumn',
                    sa.Column('id', sa.INTEGER(),
                              server_default=sa.text('nextval(\'"sampleColumn_id_seq"\'::regclass)'),
                              autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('columnType', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('file_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('comparison_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['comparison_id'], ['comparison.id'],
                                            name='sampleColumn_comparison_id_fkey', ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['file_id'], ['file.id'], name='sampleColumn_file_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='sampleColumn_pkey')
                    )
    op.create_table('rawData',
                    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"rawData_id_seq"\'::regclass)'),
                              autoincrement=True, nullable=False),
                    sa.Column('primary_id', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('gene_names', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('value', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
                    sa.Column('sampleColumn_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['sampleColumn_id'], ['sampleColumn.id'],
                                            name='rawData_sampleColumn_id_fkey', ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='rawData_pkey')
                    )

    op.create_table('quantificationMethod',
                    sa.Column('id', sa.INTEGER(),
                              server_default=sa.text('nextval(\'"quantificationMethod_id_seq"\'::regclass)'),
                              autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='quantificationMethod_project_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='quantificationMethod_pkey')
                    )

    op.create_table('keyword',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='keyword_project_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='keyword_pkey')
                    )
    op.create_table('author',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('contact', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('first', sa.BOOLEAN(), autoincrement=False, nullable=False),
                    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='author_project_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='author_pkey')
                    )


    op.create_table('pi',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('contact', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['project_id'], ['project.id'], name='pi_project_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', name='pi_pkey')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pi')
    op.drop_table('comparison')
    op.drop_table('sampleColumn')
    op.drop_table('author')
    op.drop_table('keyword')
    op.drop_table('file')
    op.drop_table('quantificationMethod')
    op.drop_table('rawData')
    op.drop_table('disease')
    op.drop_table('tissue')
    op.drop_table('cellType')
    op.drop_table('differentialAnalysisData')
    op.drop_table('sampleAnnotation')
    op.drop_table('instrument')
    op.drop_table('collaborator')
    op.drop_table('user')
    op.drop_table('organism')
    op.drop_table('project')
    # ### end Alembic commands ###
