import Anthropic from '@anthropic-ai/sdk';
import logger from '../utils/logger.js';

class ClaudeService {
  constructor() {
    this.apiKey = process.env.CLAUDE_API_KEY;
    
    if (!this.apiKey) {
      logger.warn('Claude API key not configured');
      this.client = null;
    } else {
      this.client = new Anthropic({
        apiKey: this.apiKey
      });
    }
  }

  async generatePost(theme, referencePosts = [], maxLength = 500) {
    if (!this.client) {
      throw new Error('Claude API not configured');
    }

    try {
      const systemPrompt = `あなたはThreads投稿のエキスパートです。エンゲージメントの高い魅力的な投稿を作成します。
以下の特徴を持つ投稿を作成してください：
- 読みやすく、共感を呼ぶ内容
- 適度な絵文字の使用
- ハッシュタグは最大3つまで
- ${maxLength}文字以内
- 日本語で作成`;

      let userPrompt = `テーマ: ${theme}\n\n`;
      
      if (referencePosts.length > 0) {
        userPrompt += '参考にする人気投稿:\n';
        referencePosts.forEach((post, index) => {
          userPrompt += `${index + 1}. ${post.content} (いいね: ${post.likes})\n`;
        });
        userPrompt += '\n上記の投稿の良い要素を参考にしながら、独自性のある投稿を作成してください。';
      } else {
        userPrompt += 'このテーマに関する魅力的な投稿を作成してください。';
      }

      const response = await this.client.messages.create({
        model: 'claude-3-sonnet-20240229',
        max_tokens: 1000,
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: userPrompt
          }
        ]
      });

      const generatedContent = response.content[0].text.trim();
      logger.info('Post generated successfully');
      
      return {
        content: generatedContent,
        metadata: {
          model: 'claude-3-sonnet',
          theme: theme,
          referencedPosts: referencePosts.length
        }
      };
    } catch (error) {
      logger.error('Claude API error:', error);
      throw new Error(`Failed to generate post: ${error.message}`);
    }
  }

  async improvePost(originalContent, theme = null, maxLength = 500) {
    if (!this.client) {
      throw new Error('Claude API not configured');
    }

    try {
      const systemPrompt = `あなたはThreads投稿の改善エキスパートです。
投稿をより魅力的でエンゲージメントの高いものに改善します。
- 元の意図を保ちながら改善
- ${maxLength}文字以内
- 適度な絵文字とハッシュタグ
- 日本語で作成`;

      let userPrompt = `以下の投稿を改善してください:\n\n${originalContent}`;
      
      if (theme) {
        userPrompt += `\n\nテーマ: ${theme}`;
      }

      const response = await this.client.messages.create({
        model: 'claude-3-sonnet-20240229',
        max_tokens: 1000,
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: userPrompt
          }
        ]
      });

      const improvedContent = response.content[0].text.trim();
      logger.info('Post improved successfully');
      
      return {
        original: originalContent,
        improved: improvedContent,
        metadata: {
          model: 'claude-3-sonnet',
          theme: theme
        }
      };
    } catch (error) {
      logger.error('Claude API error:', error);
      throw new Error(`Failed to improve post: ${error.message}`);
    }
  }

  async analyzePosts(posts) {
    if (!this.client) {
      throw new Error('Claude API not configured');
    }

    try {
      const systemPrompt = `あなたはソーシャルメディア分析の専門家です。
投稿のパターンと成功要因を分析します。`;

      let userPrompt = '以下の人気投稿を分析し、共通する成功要因を教えてください:\n\n';
      
      posts.forEach((post, index) => {
        userPrompt += `投稿${index + 1} (いいね: ${post.likes}):\n${post.content}\n\n`;
      });

      const response = await this.client.messages.create({
        model: 'claude-3-sonnet-20240229',
        max_tokens: 1500,
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: userPrompt
          }
        ]
      });

      const analysis = response.content[0].text.trim();
      logger.info('Posts analyzed successfully');
      
      return {
        analysis: analysis,
        postsAnalyzed: posts.length
      };
    } catch (error) {
      logger.error('Claude API error:', error);
      throw new Error(`Failed to analyze posts: ${error.message}`);
    }
  }

  async generateHashtags(content, maxHashtags = 3) {
    if (!this.client) {
      throw new Error('Claude API not configured');
    }

    try {
      const response = await this.client.messages.create({
        model: 'claude-3-sonnet-20240229',
        max_tokens: 200,
        system: `投稿内容に最適なハッシュタグを${maxHashtags}個生成してください。
各ハッシュタグは#で始まり、スペースで区切ってください。`,
        messages: [
          {
            role: 'user',
            content: `投稿内容: ${content}`
          }
        ]
      });

      const hashtags = response.content[0].text.trim();
      logger.info('Hashtags generated successfully');
      
      return hashtags;
    } catch (error) {
      logger.error('Claude API error:', error);
      throw new Error(`Failed to generate hashtags: ${error.message}`);
    }
  }
}

export default new ClaudeService();