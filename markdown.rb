# Processor for Github flavored markdown, adapted from:
# https://gist.github.com/1300939

require 'rubygems'
require 'redcarpet'
require 'albino'

def optionize(options)
  option_hash = {}
  options.each { |opt| 
    option_hash[opt] = true
  }
  option_hash
end

class SyntaxRenderer < Redcarpet::Render::HTML
  def block_code(code, language)
    if language && !language.empty?
      code = Albino.colorize(code, language)
    end
    "<div class='code-block'><pre><code>#{code}</code></pre></div>"
  end
end

def markdown(text)
  renderer = SyntaxRenderer.new(optionize [
    :with_toc_data,
    :hard_wrap,
    :xhtml
  ])
  markdown = Redcarpet::Markdown.new(renderer, optionize([
    :fenced_code_blocks,
    :no_intra_emphasis,
    :tables,
    :autolink,
    :strikethrough,
    :space_after_headers
  ]))
  markdown.render(text)
end

if __FILE__ == $0
  $stdout.print markdown( ARGF.read )
end
