# .desktop file
desktop_file =files('org.cvfosammmm.Lemma.desktop')
install_data(
  desktop_file,
  install_dir: join_paths(datadir, 'applications'),
)

# icon
install_data(
  files('org.cvfosammmm.Lemma.svg'),
  install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'),
)

# metainfo
metainfo_file = i18n.merge_file(
  input:  files('org.cvfosammmm.Lemma.metainfo.xml.in'),
  output: 'org.cvfosammmm.Lemma.metainfo.xml',
  type: 'xml',
  po_dir: join_paths(meson.project_source_root(), 'po'),
  install: true,
  install_dir: join_paths(datadir, 'metainfo'),
)
