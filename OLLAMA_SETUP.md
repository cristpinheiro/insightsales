# Ollama Model Setup

## Create the model

Run this command in your terminal to create the custom model:

```bash
ollama create insightsales-model -f Modelfile
```

## Verify the model

Check if the model was created successfully:

```bash
ollama list
```

You should see `insightsales-model` in the list.

## Test the model

Test with a simple question:

```bash
ollama run insightsales-model "Show all sellers"
```

Expected output: `SELECT id, name FROM seller ORDER BY name;`

## Use in the application

The application is configured to use this model automatically via the `OLLAMA_MODEL` setting in `.env`:

```env
OLLAMA_MODEL=insightsales-model
```

## Update the model

If you need to update the Modelfile, recreate the model:

```bash
ollama rm insightsales-model
ollama create insightsales-model -f Modelfile
```

## Alternative base models

If `llama2` is not available, you can use other models by changing the `FROM` line in Modelfile:

- `FROM codellama` - Better for code generation
- `FROM llama3` - Newer version (if available)
- `FROM mistral` - Alternative smaller model
- `FROM phi` - Lightweight option

Example:
```
FROM codellama
```

Then recreate the model with `ollama create`.
