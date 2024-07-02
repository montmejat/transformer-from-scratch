import argparse

from tinygrad import Tensor, nn

from dataset import TinyShakespeare
from models import Bigram, Transfomer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model", choices=["bigram", "transformer"], default="transformer"
    )
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--sequence-length", type=int, default=32)
    parser.add_argument("--embed-size", type=int, default=16)
    args = parser.parse_args()

    match args.model:
        case "bigram":
            model = Bigram(vocab_size=len(TinyShakespeare._vocab))
        case "transformer":
            model = Transfomer(
                vocab_size=len(TinyShakespeare._vocab),
                sequence_length=args.sequence_length,
                embed_size=args.embed_size,
            )

    train_length = len(TinyShakespeare._train_tokens)
    val_length = len(TinyShakespeare._val_tokens)
    total_length = train_length + val_length

    print(f"Train: {train_length} tokens ({train_length / total_length:.1%})")
    print(f"Val: {val_length} tokens ({val_length / total_length:.1%})")

    x, y = TinyShakespeare.get_random_batch("train")

    print("x:", x.numpy())
    print("y:", y.numpy())

    text = model.yap(0, length=100)
    print(text.shape)

    for token in text.squeeze():
        print(TinyShakespeare._token_to_char[token.item()], end="")

    optimizer = nn.optim.AdamW(model.weight, lr=0.01)

    with Tensor.train():
        for steps in range(3000):
            x, y = TinyShakespeare.get_random_batch(
                "train",
                batch_size=args.batch_size,
                sequence_length=args.sequence_length,
            )

            out = model(x)
            batch, sequence_length, vocab_size = out.shape
            logits = out.view(batch * sequence_length, len(TinyShakespeare._vocab))

            target = y.view(batch * sequence_length, 1)
            loss = logits.sparse_categorical_crossentropy(target) / target.shape[0]

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if steps % 100 == 0:
                print(f"step {steps}, loss: {loss.numpy()}")

    text = model.yap(0, length=100)

    for token in text:
        print(TinyShakespeare._token_to_char[token], end="")