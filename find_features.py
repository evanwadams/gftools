
import contextlib
import os


from fontTools import ttLib

from google.apputils import app

from util import google_fonts as fonts


def ListFeatures(font, table, name_fn):
  """List features for specified font. Table assumed structured like GPS/GSUB.

  Args:
    font: a TTFont.
    table: name of table.
    name_fn: function to resolve lookup type => name.
  Returns:
    List of 3-tuples of ('GPOS', tag, name) of the features in the font.
  """
  results = []
  if table not in font:
    return results

  tab = font[table].table
  if not tab or not tab.LookupList or not tab.LookupList.Lookup:
    return results
  lookups = tab.LookupList.Lookup

  for feat in tab.FeatureList.FeatureRecord:
    tag = feat.FeatureTag
    for idx in feat.Feature.LookupListIndex:
      lookup_name = name_fn(lookups[idx].LookupType)
      results.append((table, tag, lookup_name))

  return results


def FindFonts(path):
  """Find one weight per family in each font directory in path.

  Args:
    path: A directory.
  Returns:
    A list of full paths to font files in Google-fonts style directories under
    path. Selects one weight per family.
  """
  files = []
  for font_dir in fonts.FontDirs(path):
    try:
      metadata = fonts.Metadata(font_dir)
    except ValueError:
      print 'Bad METADATA.pb for %s' % font_dir
      continue

    try:
      filename = fonts.RegularWeight(metadata)
    except OSError:
      print 'No RegularWeight for %s' % font_dir
      filename = metadata.fonts[0].filename

    files.append(os.path.join(font_dir, filename))

  return files


def main(argv):
  for path in argv[1:]:
    font_files = [path]
    if os.path.isdir(path):
      font_files = FindFonts(path)

    for font_file in font_files:
      features = []
      try:
        with contextlib.closing(ttLib.TTFont(font_file)) as font:
          features += ListFeatures(font, 'GSUB', fonts.GsubLookupTypeName)
          features += ListFeatures(font, 'GPOS', fonts.GposLookupTypeName)
      except IOError:
        print '%s does not exist or is not a valid font' % font_file
      for (table, tag, lookup_name) in features:
        print '{:32s} {:4s} {:8s} {:15s}'.format(
            os.path.basename(font_file), table, str(tag), lookup_name)


if __name__ == '__main__':
  app.run()
