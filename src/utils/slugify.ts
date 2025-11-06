// ABOUTME: Slug generation utility

export function slugify(text: string, maxLength: number = 50): string {
  // Convert to lowercase and replace spaces with dashes
  let slug = text
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '');

  // Remove consecutive dashes
  slug = slug.replace(/-+/g, '-');

  // Truncate at word boundary
  if (slug.length > maxLength) {
    slug = slug.substring(0, maxLength);
    const lastDash = slug.lastIndexOf('-');
    if (lastDash > maxLength * 0.6) {
      slug = slug.substring(0, lastDash);
    }
  }

  // Remove trailing dash
  slug = slug.replace(/-$/, '');

  return slug;
}
