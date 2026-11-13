import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export function Markdown({ children }: { children: string }) {
  return (
    <div className="markdown">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: (props) => {
            const { node, ...rest } = props
            void node
            return <a {...rest} target="_blank" rel="noreferrer" />
          },
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  )
}
