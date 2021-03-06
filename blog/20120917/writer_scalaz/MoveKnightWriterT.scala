package fits.sample

import scalaz._
import Scalaz._
import WriterT._

object MoveKnightWriterT extends App {

	type KnightPos = Tuple2[Int, Int]

	val moveKnight = (p: KnightPos) => List(
		(p._1 + 2, p._2 - 1), (p._1 + 2, p._2 + 1),
		(p._1 - 2, p._2 - 1), (p._1 - 2, p._2 + 1),
		(p._1 + 1, p._2 - 2), (p._1 + 1, p._2 + 2),
		(p._1 - 1, p._2 - 2), (p._1 - 1, p._2 + 2)
	).filter { case (x, y) => 1 <= x && x <= 8 && 1 <= y && y <= 8 }

	val moveKnightWriter = (p: KnightPos) => {
		val list = moveKnight(p).map {np =>
			(s" -> $np", np)
		}
		writerT(list)
	}

	val inMany = (x: Int) => (start: KnightPos) => {
		val stWriter = writerT((s"$start", start) :: Nil)
		// 以下でも同じ
		//val stWriter = writerT(List((s"$start", start)))

		stWriter >>= List.fill(x){ moveKnightWriter }.reduceRight {(a, b) =>
			(p: KnightPos) => b(p) >>= a
		}
	}

	val routeReachIn = (x: Int) => (start: KnightPos, end: KnightPos) =>
		inMany(x)(start).run.filter { _._2 == end } map { _._1 }

	routeReachIn(3)((6, 2), (6, 1)).foreach {println}
	println("-----")
	routeReachIn(3)((6, 2), (7, 3)).foreach {println}
}
